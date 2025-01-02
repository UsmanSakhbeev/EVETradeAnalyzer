import json
import os
import time
from datetime import timedelta
from decimal import Decimal

import requests
from django.db.models import Max
from django.utils.timezone import now

from evetradeanalyzer.trade_analysis.models import Item, MarketOrder


def fetch_market_data():
    base_url = "https://esi.evetech.net/latest/markets/10000002/orders/"
    station_id = 60003760  # ID Jita IV - Moon 4 - Caldari Navy Assembly Plant
    all_orders = []

    response = requests.get(base_url)
    response.raise_for_status()
    total_pages = int(response.headers.get("X-Pages", 1))

    for page in range(1, total_pages + 1):  # Загружаем все страницы
        params = {"page": page}
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        page_orders = response.json()

        station_orders = [
            order for order in page_orders if order["location_id"] == station_id
        ]
        all_orders.extend(station_orders)

    return all_orders


def fetch_and_save_market_data():
    base_url = "https://esi.evetech.net/latest/markets/10000002/orders/"
    all_orders = []

    # Создаем директорию для временных данных
    temp_dir = "temp_market_data"
    os.makedirs(temp_dir, exist_ok=True)

    # Загружаем уже сохранённые страницы, если есть
    processed_pages = 0
    if os.path.exists("market_data.json"):
        with open("market_data.json", "r") as f:
            all_orders = json.load(f)
        processed_pages = len(all_orders) // 1000  # Примерно 1000 записей на страницу
        print(f"Loaded {len(all_orders)} orders from local cache.")

    print(f"Starting from page {processed_pages + 1}...")

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        total_pages = int(response.headers.get("X-Pages", 1))

        for page in range(processed_pages + 1, total_pages + 1):
            print(f"Fetching page {page}/{total_pages}...")
            params = {"page": page}
            retries = 3

            while retries > 0:
                try:
                    response = requests.get(base_url, params=params)
                    response.raise_for_status()
                    page_orders = response.json()

                    # Добавляем проверку на наличие даты и обрабатываем ордеры
                    for order in page_orders:
                        # Если даты нет, устанавливаем текущую дату и время
                        order["issued"] = order.get("issued", None)

                    # Сохраняем каждую страницу в отдельный файл
                    with open(f"{temp_dir}/page_{page}.json", "w") as temp_file:
                        json.dump(page_orders, temp_file)

                    all_orders.extend(page_orders)
                    break
                except requests.exceptions.RequestException as e:
                    retries -= 1
                    print(
                        f"Ошибка при запросе страницы {page}: {e}. Повтор через 5 секунд..."
                    )
                    time.sleep(5)

            if retries == 0:
                print(f"Не удалось загрузить страницу {page}. Пропускаем...")

        # После сбора всех данных объединяем и сохраняем их в основной файл
        print("Combining and saving all fetched data...")
        with open("market_data.json", "w") as f:
            json.dump(all_orders, f)

        print(f"Successfully fetched and saved {len(all_orders)} orders!")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return None

    return all_orders


def load_market_data():
    try:
        with open("market_data.json", "r") as f:
            all_orders = json.load(f)
        print(f"Loaded {len(all_orders)} orders from local cache.")
        return all_orders
    except FileNotFoundError:
        print(
            "Файл market_data.json не найден. Сначала выполните fetch_and_save_market_data."
        )
        return None


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


def find_profitable_deals(threshold=0.35, days=3):
    """
    Ищет выгодные сделки, сравнивая минимальную цену продажи с предыдущей минимальной ценой,
    а также фильтрует результаты по времени (последние `days` дней) по полю last_price.
    """
    # Вычисляем дату начала анализа с учетом часового пояса
    recent_date = now() - timedelta(days=days)
    profitable_deals = []

    # Получаем все уникальные товары с ордерами на продажу
    items_with_orders = (
        MarketOrder.objects.filter(is_buy_order=False)
        .values_list("item_id", flat=True)
        .distinct()
    )

    for item_id in items_with_orders:
        # Находим две минимальные цены на продажу для данного товара
        last_orders = MarketOrder.objects.filter(
            item_id=item_id, is_buy_order=False
        ).order_by("price")[:2]

        if len(last_orders) < 2:
            continue  # Если меньше двух ордеров, пропускаем

        # Последняя и предпоследняя минимальные цены продажи
        last_order = last_orders[0]
        prev_order = last_orders[1]
        last_price = last_order.price
        prev_price = prev_order.price

        # Находим максимальную цену покупки для данного товара
        max_buy_price = MarketOrder.objects.filter(
            item_id=item_id, is_buy_order=True
        ).aggregate(Max("price"))["price__max"]

        # Если максимальная цена покупки отсутствует, пропускаем товар
        if not max_buy_price:
            continue

        # Рассчитываем процент выгоды
        profit_percent = ((prev_price / last_price) - 1) * 100 if last_price > 0 else 0
        profit_percent = round(profit_percent, 2)

        # Проверяем, выгодна ли сделка
        if prev_price > last_price * Decimal(1 + threshold):
            # Сохраняем только те сделки, где last_order был выставлен в последние `days` дней
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

    # Сортировка по проценту выгоды (в убывающем порядке)
    profitable_deals.sort(key=lambda x: x["profit_percent"], reverse=True)

    return profitable_deals


def save_orders_to_db(all_orders):
    MarketOrder.objects.all().delete()
    print("SCP [ДАННЫЕ УДАЛЕНЫ]")

    items_cache = {}  # Кэш для уже созданных Item
    market_orders = []  # Список для массового добавления ордеров

    for order in all_orders:
        # Получаем или создаём запись для товара
        item_id = order["type_id"]
        if item_id not in items_cache:
            item, _ = Item.objects.get_or_create(
                id=item_id, defaults={"name": f"Item {item_id}"}
            )
            items_cache[item_id] = item
        else:
            item = items_cache[item_id]

        # Добавляем объект MarketOrder в список
        market_orders.append(
            MarketOrder(
                item=item,
                price=order["price"],
                volume_remain=order["volume_remain"],
                is_buy_order=order["is_buy_order"],
                issued=order["issued"],
            )
        )

    # Используем bulk_create для массовой вставки данных
    MarketOrder.objects.bulk_create(market_orders)
    print(f"Сохранено {len(all_orders)} ордеров в базу данных.")
