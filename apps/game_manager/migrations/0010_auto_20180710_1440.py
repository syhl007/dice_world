# Generated by Django 2.0.4 on 2018-07-10 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_manager', '0009_auto_20180710_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='pic',
            field=models.ImageField(default='static/resource/items/default/no_img.jpg', upload_to='static/resource/items/', verbose_name='物品图片'),
        ),
    ]