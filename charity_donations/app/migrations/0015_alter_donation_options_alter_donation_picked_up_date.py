# Generated by Django 4.2.3 on 2023-07-14 09:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_donation_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={},
        ),
        migrations.AlterField(
            model_name='donation',
            name='picked_up_date',
            field=models.DateField(blank=True, default=datetime.date(2000, 1, 1), null=True),
        ),
    ]