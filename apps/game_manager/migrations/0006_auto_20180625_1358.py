# Generated by Django 2.0.4 on 2018-06-25 13:58

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import game_manager.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_manager', '0005_room_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.UUIDField(default=game_manager.models.create_uuid, primary_key=True, serialize=False, verbose_name='UUID')),
                ('name', models.CharField(max_length=127, verbose_name='任务模组名')),
                ('description', models.TextField(verbose_name='描述')),
                ('map', models.ImageField(null=True, upload_to='resource/game/maps/', verbose_name='地图')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.UUIDField(default=game_manager.models.create_uuid, primary_key=True, serialize=False, verbose_name='UUID')),
                ('name', models.CharField(max_length=127, verbose_name='物品名称')),
                ('file', models.FileField(upload_to='resource/game/items/', verbose_name='物品资料文件')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=game_manager.models.create_uuid, primary_key=True, serialize=False, verbose_name='UUID')),
                ('name', models.CharField(max_length=127, verbose_name='任务模组名')),
                ('init_file', models.FileField(upload_to='resource/game/tasks/', verbose_name='任务模组文件')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者')),
            ],
        ),
        migrations.CreateModel(
            name='TaskRecord',
            fields=[
                ('id', models.UUIDField(default=game_manager.models.create_uuid, primary_key=True, serialize=False, verbose_name='UUID')),
                ('done', models.BooleanField(default=False, verbose_name='是否完成')),
                ('file', models.FileField(null=True, upload_to='resource/game/records/', verbose_name='日志记录')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='更新时间')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room+', to='game_manager.Room', verbose_name='房间')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='game_manager.Task', verbose_name='任务')),
            ],
        ),
        migrations.AlterField(
            model_name='character',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者'),
        ),
        migrations.AlterField(
            model_name='character',
            name='detail',
            field=models.FileField(upload_to='templates/character/head/', verbose_name='角色资料文件'),
        ),
        migrations.AlterField(
            model_name='character',
            name='head',
            field=models.ImageField(default='resource/character/head/default/no_img.jpg', upload_to='resource/character/head/', verbose_name='角色头像'),
        ),
    ]
