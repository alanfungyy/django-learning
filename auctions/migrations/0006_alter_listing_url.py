# Generated by Django 3.2.7 on 2021-10-20 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.URLField(blank=True, max_length=256, verbose_name='URL'),
        ),
    ]