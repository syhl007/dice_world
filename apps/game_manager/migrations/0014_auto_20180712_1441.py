# Generated by Django 2.0.4 on 2018-07-12 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0013_auto_20180711_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='areas',
            field=models.ManyToManyField(related_name='room_area', to='game_manager.Area', verbose_name='地区列表'),
        ),
        migrations.AddField(
            model_name='room',
            name='items',
            field=models.ManyToManyField(related_name='room_item', to='game_manager.Item', verbose_name='物品列表'),
        ),
        migrations.AddField(
            model_name='room',
            name='tasks',
            field=models.ManyToManyField(related_name='room_task', to='game_manager.Task', verbose_name='任务列表'),
        ),
        migrations.AlterField(
            model_name='room',
            name='npcs',
            field=models.ManyToManyField(related_name='room_npc', to='game_manager.Character', verbose_name='NPC列表'),
        ),
    ]