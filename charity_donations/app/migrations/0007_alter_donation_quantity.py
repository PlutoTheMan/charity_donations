# Generated by Django 4.2.3 on 2023-07-11 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_donation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
