# Generated by Django 2.2.10 on 2020-09-08 19:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0010_auto_20200907_1702'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('name',)},
        ),
    ]
