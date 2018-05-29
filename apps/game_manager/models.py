import uuid
import time

from datetime import datetime
from django.db import models

from user_manager.models import User


def create_uuid(key=None):
    if key is None:
        key = str(time.time())
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name=key))


class Room(models.Model):
    id = models.CharField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    # num = models.CharField(verbose_name=u"房间号", nax_length=64, unique=True, null=False, default=)
    name = models.CharField(verbose_name=u"房间名", max_length=64, default=str(time.time()))
    gm = models.ForeignKey(verbose_name=u"GM", to=User, on_delete=models.CASCADE)
    tag = models.CharField(verbose_name=u"标签", max_length=127, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"房间"
        verbose_name_plural = verbose_name


class Group(models.Model):
    id = models.CharField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    users = models.ManyToManyField(verbose_name=u"玩家列表", to=User, through='GroupMember')
    room = models.ForeignKey(verbose_name=u"所属房间", to=Room, on_delete=models.CASCADE)
    # 0——旁观者
    # 1——游戏参与者
    type = models.SmallIntegerField(verbose_name=u"队伍类型", default=0)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队"
        verbose_name_plural = verbose_name


class Character(models.Model):
    id = models.CharField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"角色姓名", null=False, blank=True)
    head = models.ImageField(verbose_name=u"角色头像", default="templates/character/default/no_img.jpg")
    detail = models.FileField(verbose_name=u"角色资料文件")
    user = models.ForeignKey(verbose_name=u"上传者", to=User, on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)
    update_user = models.ForeignKey(verbose_name=u"修改者", to=User, on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name=u"更新时间", default=datetime.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"游戏角色"
        verbose_name_plural = verbose_name


class GroupMember(models.Model):
    id = models.CharField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    user = models.ForeignKey(verbose_name=u"用户", to=User, on_delete=models.CASCADE)
    group = models.ForeignKey(verbose_name=u"团队", to=Group, on_delete=models.CASCADE)
    character = models.ForeignKey(verbose_name=u"角色", to=Character, null=True, on_delete=models.CASCADE)
    is_leader = models.BooleanField(verbose_name=u"队长", default=False)
    tag = models.CharField(verbose_name=u"标签", max_length=127)
    add_time = models.DateTimeField(verbose_name=u"加入时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队信息"
        verbose_name_plural = verbose_name


class GameTxt(models.Model):
    id = models.CharField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    user = models.ForeignKey(verbose_name=u"上传者", to=User, on_delete=models.CASCADE)
    file = models.FileField(verbose_name=u"游戏记录文件")
    add_time = models.DateTimeField(verbose_name=u"加入时间", default=datetime.now)

    class Meta:
        verbose_name = u"游戏文本信息"
        verbose_name_plural = verbose_name
