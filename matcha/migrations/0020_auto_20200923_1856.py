# Generated by Django 2.2.10 on 2020-09-23 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0019_auto_20200923_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='latitude',
            field=models.FloatField(default=0.0, verbose_name='широта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='longitude',
            field=models.FloatField(default=0.0, verbose_name='долгота'),
        ),
    ]
