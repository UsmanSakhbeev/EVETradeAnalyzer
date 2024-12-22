# Generated by Django 5.1.4 on 2024-12-20 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade_analysis', '0002_alter_item_name_alter_marketorder_is_buy_order_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfitableDeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255)),
                ('last_price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('prev_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('price_difference', models.DecimalField(decimal_places=2, max_digits=20)),
                ('profit_percent', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_buy_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('volume_remain', models.IntegerField()),
            ],
        ),
    ]
