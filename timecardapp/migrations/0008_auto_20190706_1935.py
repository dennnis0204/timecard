# Generated by Django 2.2.1 on 2019-07-06 19:35

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timecardapp', '0007_preferences'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Preferences',
            new_name='Settings',
        ),
    ]
