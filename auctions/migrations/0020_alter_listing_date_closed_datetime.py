# Generated by Django 4.0.2 on 2022-02-20 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0019_alter_listing_date_closed_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='date_closed_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]