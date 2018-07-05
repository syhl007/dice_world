# Generated by Django 2.0.4 on 2018-07-05 09:35

import datetime
import dice_world.standard
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0003_auto_20180704_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomItemRecord',
            fields=[
                ('id', models.UUIDField(default=dice_world.standard.create_uuid, primary_key=True, serialize=False, verbose_name='UUID')),
                ('private', models.BooleanField(default=False, verbose_name='是否公开')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='物品描述'),
        ),
        migrations.AddField(
            model_name='item',
            name='unique',
            field=models.BooleanField(default=False, verbose_name='是否唯一'),
        ),
        migrations.AlterField(
            model_name='item',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='static/resource/game/items/', verbose_name='物品资料文件'),
        ),
        migrations.AddField(
            model_name='roomitemrecord',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_manager.Item', verbose_name='物品'),
        ),
        migrations.AddField(
            model_name='roomitemrecord',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_manager.Character', verbose_name='玩家'),
        ),
        migrations.AddField(
            model_name='roomitemrecord',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_manager.Room', verbose_name='房间'),
        ),
    ]
