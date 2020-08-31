# Generated by Django 2.2.10 on 2020-08-29 21:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0006_auto_20200828_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersConnect',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('user_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_1_set', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь 1')),
                ('user_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_2_set', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь 2')),
            ],
            options={
                'verbose_name': 'Коннект пользователей',
                'verbose_name_plural': 'Коннекты пользователей',
                'unique_together': {('user_1', 'user_2')},
            },
        ),
    ]