# Generated by Django 2.0.4 on 2018-07-03 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者'),
        ),
        migrations.AddField(
            model_name='room',
            name='gm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gm', to=settings.AUTH_USER_MODEL, verbose_name='GM'),
        ),
        migrations.AddField(
            model_name='item',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='character',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='character', to='game_manager.Character', verbose_name='角色'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group', to='game_manager.Group', verbose_name='团队'),
        ),
        migrations.AddField(
            model_name='groupmember',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='group',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room', to='game_manager.Room', verbose_name='所属房间'),
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(through='game_manager.GroupMember', to=settings.AUTH_USER_MODEL, verbose_name='玩家列表'),
        ),
        migrations.AddField(
            model_name='gametxt',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user+', to=settings.AUTH_USER_MODEL, verbose_name='上传者'),
        ),
        migrations.AddField(
            model_name='character',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者'),
        ),
        migrations.AddField(
            model_name='character',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editor', to=settings.AUTH_USER_MODEL, verbose_name='修改者'),
        ),
        migrations.AddField(
            model_name='area',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator+', to=settings.AUTH_USER_MODEL, verbose_name='创作者'),
        ),
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together={('user', 'group')},
        ),
    ]