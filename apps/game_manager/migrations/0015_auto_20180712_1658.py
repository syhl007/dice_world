# Generated by Django 2.0.4 on 2018-07-12 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0014_auto_20180712_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomitemrecord',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_item_record', to='game_manager.Item', verbose_name='物品'),
        ),
    ]