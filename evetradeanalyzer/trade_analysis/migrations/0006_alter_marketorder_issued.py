# Generated by Django 5.1.4 on 2024-12-21 13:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade_analysis', '0005_marketorder_issued'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketorder',
            name='issued',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]