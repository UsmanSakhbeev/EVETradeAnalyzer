# Generated by Django 5.1.4 on 2024-12-21 13:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade_analysis', '0004_alter_profitabledeal_profit_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketorder',
            name='issued',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
