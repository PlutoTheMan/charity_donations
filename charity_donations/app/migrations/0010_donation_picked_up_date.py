# Generated by Django 4.2.3 on 2023-07-14 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_donation_picked_up'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='picked_up_date',
            field=models.DateField(null=True),
        ),
    ]
