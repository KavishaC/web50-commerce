# Generated by Django 3.1.4 on 2021-03-22 10:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20210301_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='date_closed',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
