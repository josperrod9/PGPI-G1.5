# Generated by Django 2.2 on 2022-11-26 13:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0015_auto_20221126_1222'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Responses',
            new_name='Response',
        ),
    ]