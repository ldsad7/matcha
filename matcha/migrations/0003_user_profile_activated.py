# Generated by Django 2.2.10 on 2020-08-28 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0002_auto_20200826_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_activated',
            field=models.BooleanField(default=False, verbose_name='профиль активирован'),
        ),
    ]
