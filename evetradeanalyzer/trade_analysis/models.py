from django.db import models
from django.utils.timezone import now


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)  # Индексируем name
    average_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return self.name


class MarketOrder(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    volume_remain = models.IntegerField()
    is_buy_order = models.BooleanField(db_index=True)
    issued = models.DateTimeField(default=now)  # Используем timezone.now

    class Meta:
        indexes = [
            models.Index(fields=["item", "price"]),
        ]

    def __str__(self):
        return f"{self.item.name} - {self.price}"


class ProfitableDeal(models.Model):
    item_name = models.CharField(max_length=255)
    last_price = models.DecimalField(max_digits=20, decimal_places=2)
    prev_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    price_difference = models.DecimalField(max_digits=20, decimal_places=2)
    profit_percent = models.DecimalField(max_digits=15, decimal_places=2)  # Увеличено
    max_buy_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    volume_remain = models.IntegerField()

    def __str__(self):
        return f"{self.item_name} - {self.profit_percent}%"
