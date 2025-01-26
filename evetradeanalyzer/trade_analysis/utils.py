import json
import os
import shutil
import time
import traceback
from datetime import timedelta
from decimal import Decimal

import requests
from django.db import transaction
from django.db.models import Max
from django.utils.timezone import now

from evetradeanalyzer.trade_analysis.models import Item, MarketOrder, ProfitableDeal


def fetch_and_process_data_task():
    while True:
        success = fetch_and_save_orders_to_db()
        if not success:
            print("Не удалось загрузить данные. Повтор через 30 секунд.")
            time.sleep(30)
            continue

        profitable_deals = find_profitable_deals(threshold=0.35)
        ProfitableDeal.objects.all().delete()

        ProfitableDeal.objects.bulk_create(
            [
                ProfitableDeal(
                    item_name=deal["item_name"],
                    last_price=deal["last_price"],
                    prev_price=deal["prev_price"],
                    price_difference=deal["price_difference"],
                    profit_percent=deal["profit_percent"],
                    max_buy_price=deal["max_buy_price"],
                    volume_remain=deal["volume_remain"],
                )
                for deal in profitable_deals
            ]
        )

        print(f"Сохранено {len(profitable_deals)} выгодных сделок в базу данных.")
        time.sleep(720)  # Ожидание перед повторным запуском


def fetch_and_save_orders_to_db(batch_size=10000):
    base_url = "https://esi.evetech.net/latest/markets/10000002/orders/"
    print("Начало загрузки и сохранения ордеров в базу данных...")

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        total_pages = int(response.headers.get("X-Pages", 1))

        MarketOrder.objects.all().delete()
        print("Существующие данные MarketOrder удалены.")

        items_cache = {}
        market_orders = []  # Для накопления данных из нескольких страниц

        for page in range(1, total_pages + 1):
            print(f"Загрузка страницы {page}/{total_pages}...")
            retries = 3

            while retries > 0:
                try:
                    response = requests.get(base_url, params={"page": page})
                    response.raise_for_status()
                    page_orders = response.json()

                    for order in page_orders:
                        item_id = order["type_id"]
                        if item_id not in items_cache:
                            item, _ = Item.objects.get_or_create(
                                id=item_id, defaults={"name": f"Item {item_id}"}
                            )
                            items_cache[item_id] = item
                        else:
                            item = items_cache[item_id]

                        market_orders.append(
                            MarketOrder(
                                item=item,
                                price=order["price"],
                                volume_remain=order["volume_remain"],
                                is_buy_order=order["is_buy_order"],
                                issued=order.get("issued", None),
                            )
                        )

                    # Сохранение данных, если накопился батч
                    if len(market_orders) >= batch_size:
                        with transaction.atomic():
                            MarketOrder.objects.bulk_create(market_orders)
                        print(f"Сохранено {len(market_orders)} записей.")
                        market_orders = []  # Очистка для нового батча

                    break

                except requests.exceptions.RequestException as e:
                    retries -= 1
                    print(
                        f"Ошибка при загрузке страницы {page}: {e}. Повтор через 5 секунд..."
                    )
                    time.sleep(5)

            if retries == 0:
                print(f"Не удалось загрузить страницу {page}. Пропускаем...")

        # Сохранение оставшихся данных
        if market_orders:
            with transaction.atomic():
                MarketOrder.objects.bulk_create(market_orders)
            print(f"Сохранено {len(market_orders)} записей (остаток).")

        print("Загрузка и сохранение ордеров завершены.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке данных: {e}")
        return False


def find_profitable_deals(threshold=0.35, days=3):
    recent_date = now() - timedelta(days=days)
    profitable_deals = []

    items_with_orders = (
        MarketOrder.objects.filter(is_buy_order=False)
        .values_list("item_id", flat=True)
        .distinct()
    )

    for item_id in items_with_orders:
        last_orders = MarketOrder.objects.filter(
            item_id=item_id, is_buy_order=False
        ).order_by("price")[:2]

        if len(last_orders) < 2:
            continue

        last_order = last_orders[0]
        prev_order = last_orders[1]
        last_price = last_order.price
        prev_price = prev_order.price

        max_buy_price = MarketOrder.objects.filter(
            item_id=item_id, is_buy_order=True
        ).aggregate(Max("price"))["price__max"]

        if not max_buy_price:
            continue

        profit_percent = ((prev_price / last_price) - 1) * 100 if last_price > 0 else 0
        profit_percent = round(profit_percent, 2)

        if prev_price > last_price * Decimal(1 + threshold):
            if (
                last_order.issued >= recent_date
                and profit_percent <= 10000
                and prev_price - last_price > 1000000
                and (last_price / max_buy_price - 1) <= 0.5
                and (prev_price - last_price) * last_order.volume_remain > 1000000
            ):
                profitable_deals.append(
                    {
                        "item_name": last_order.item.name,
                        "last_price": last_price,
                        "prev_price": prev_price,
                        "volume_remain": last_order.volume_remain,
                        "price_difference": prev_price - last_price,
                        "profit_percent": profit_percent,
                        "max_buy_price": max_buy_price,
                    }
                )

    profitable_deals.sort(key=lambda x: x["profit_percent"], reverse=True)

    return profitable_deals


def update_item_names():
    base_url = "https://esi.evetech.net/latest/universe/types/"
    items = Item.objects.filter(name__startswith="Item")

    for item in items:
        try:
            response = requests.get(f"{base_url}{item.id}/")
            response.raise_for_status()
            data = response.json()
            name = data.get("name", f"Item {item.id}")
            item.name = name
            item.save()
            print(f"Название обновлено: {item.id} -> {item.name}")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при обновлении названия для {item.id}: {e}")
