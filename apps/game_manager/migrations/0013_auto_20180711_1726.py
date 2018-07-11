# Generated by Django 2.0.4 on 2018-07-11 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0012_room_npcs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='npcs',
            field=models.ManyToManyField(blank=True, null=True, related_name='npc_room', to='game_manager.Character', verbose_name='NPC列表'),
        ),
    ]
