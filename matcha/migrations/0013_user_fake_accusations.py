# Generated by Django 2.2.10 on 2020-09-21 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0012_userphoto_main'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fake_accusations',
            field=models.IntegerField(default=0, verbose_name='количество обвинения в фейковости'),
        ),
    ]
