# Generated by Django 2.0.4 on 2018-06-13 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0004_auto_20180611_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='state',
            field=models.SmallIntegerField(default=0, verbose_name='房间状态'),
        ),
    ]
