# Generated by Django 2.2.10 on 2020-09-21 15:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import matcha.models
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('matcha', '0013_user_fake_accusations'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersFake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('user_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_fake_1_set', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь 1')),
                ('user_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_fake_2_set', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь 2')),
            ],
            options={
                'verbose_name': 'Fake-коннект пользователей',
                'verbose_name_plural': 'Fake-коннекты пользователей',
                'unique_together': {('user_1', 'user_2')},
            },
            bases=(matcha.models.ManagedModel, models.Model, matcha.models.GetById),
        ),
    ]