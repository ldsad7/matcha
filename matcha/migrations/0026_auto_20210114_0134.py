# Generated by Django 2.2.10 on 2021-01-13 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0025_user_last_online'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
