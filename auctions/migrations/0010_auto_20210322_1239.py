# Generated by Django 3.1.4 on 2021-03-22 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20210322_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='created',
            new_name='created_datetime',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='created',
            new_name='created_datetime',
        ),
    ]
