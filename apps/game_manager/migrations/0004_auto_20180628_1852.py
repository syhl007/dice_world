# Generated by Django 2.0.4 on 2018-06-28 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0003_auto_20180628_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='background',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='游戏背景描述'),
        ),
    ]
