# Generated by Django 2.2.10 on 2020-09-14 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0011_auto_20200908_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='userphoto',
            name='main',
            field=models.BooleanField(default=False, verbose_name='главное'),
        ),
    ]