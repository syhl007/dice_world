# Generated by Django 2.0.4 on 2018-07-11 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0011_auto_20180710_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='npcs',
            field=models.ManyToManyField(blank=True, null=True, related_name='npc', to='game_manager.Character', verbose_name='NPC列表'),
        ),
    ]
