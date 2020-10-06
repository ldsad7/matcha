# Generated by Django 2.2.10 on 2020-09-03 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0008_auto_20200901_1851'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='latitude',
            field=models.DecimalField(decimal_places=6, default=0.0, max_digits=8, verbose_name='широта'),
        ),
        migrations.AddField(
            model_name='user',
            name='longitude',
            field=models.DecimalField(decimal_places=6, default=0.0, max_digits=9, verbose_name='долгота'),
        ),
    ]