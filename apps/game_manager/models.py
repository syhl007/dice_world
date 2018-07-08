import random
import time
import uuid
from datetime import datetime

from django.db import models

from dice_world.standard import JSONField, create_uuid, create_id
from user_manager.models import User


class Room(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    num = models.CharField(verbose_name=u"房间号", max_length=64, unique=True, null=False, default=create_id)
    name = models.CharField(verbose_name=u"房间名", max_length=64, default=time.time)
    gm = models.ForeignKey(verbose_name=u"GM", to=User, related_name="gm", on_delete=models.CASCADE)
    # 0——游戏准备中
    # 1——游戏进行中
    # -1——游戏结束
    state = models.SmallIntegerField(verbose_name=u"房间状态", default=0)
    password = models.CharField(verbose_name=u"房间密码", max_length=10, null=True, blank=True, default=None)
    sidelines = models.BooleanField(verbose_name=u"允许旁观", default=False)
    background = models.CharField(verbose_name=u"游戏背景描述", max_length=256, null=True, blank=True)
    tag = JSONField(verbose_name=u"标签", null=True, blank=True)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    def __str__(self):
        return '[' + self.num + ']' + self.name

    class Meta:
        verbose_name = u"房间"
        verbose_name_plural = verbose_name


class Group(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    users = models.ManyToManyField(verbose_name=u"玩家列表", related_name='group_player', to=User, through='GroupMember')
    room = models.ForeignKey(verbose_name=u"所属房间", to=Room, related_name="room", on_delete=models.CASCADE)
    # 0——游戏参与者
    # 1——旁观者
    # 2——申请加入者
    type = models.SmallIntegerField(verbose_name=u"队伍类型", default=0)
    send_msg = models.BooleanField(verbose_name=u"允许发言", default=True)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队"
        verbose_name_plural = verbose_name


class Character(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"角色姓名", max_length=64)
    sex = models.SmallIntegerField(verbose_name=u"角色性别", default=0)  # 0-男|1-女|2-其他
    head = models.ImageField(verbose_name=u"角色头像", upload_to="static/resource/character/head/",
                             default="static/resource/character/head/default/no_img.jpg")
    detail = models.FileField(verbose_name=u"角色资料文件", upload_to="static/resource/character/detail/")
    creator = models.ForeignKey(verbose_name=u"创作者", to=User, related_name='character_creator',
                                on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)
    editor = models.ForeignKey(verbose_name=u"修改者", to=User, related_name='character_editor', on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name=u"更新时间", auto_now=True)
    private = models.BooleanField(verbose_name=u"私人角色", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"游戏角色"
        verbose_name_plural = verbose_name


class GroupMember(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    user = models.ForeignKey(verbose_name=u"用户", to=User, related_name="group_member", on_delete=models.CASCADE)
    group = models.ForeignKey(verbose_name=u"团队", to=Group, related_name="group", on_delete=models.CASCADE)
    character = models.ForeignKey(verbose_name=u"角色", to=Character, related_name="group_character", null=True,
                                  on_delete=models.CASCADE)
    is_leader = models.BooleanField(verbose_name=u"队长", default=False)
    send_msg = models.BooleanField(verbose_name=u"允许发言", default=True)
    is_gamer = models.BooleanField(verbose_name=u"玩家", default=True)
    is_online = models.BooleanField(verbose_name=u"是否在线", default=False)
    tag = JSONField(verbose_name=u"标签", max_length=127, null=True, blank=True)
    add_time = models.DateTimeField(verbose_name=u"加入时间", default=datetime.now)
    login_time = models.DateTimeField(verbose_name=u"登录时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队信息"
        verbose_name_plural = verbose_name
        unique_together = ('user', 'group',)


class Area(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"任务模组名", max_length=127)
    creator = models.ForeignKey(verbose_name=u"创作者", to=User, related_name='area_creator', on_delete=models.CASCADE)
    description = models.TextField(verbose_name=u"描述")
    map = models.ImageField(verbose_name=u"地图", upload_to="static/resource/game/maps/", null=True)
    private = models.BooleanField(verbose_name=u"是否公开", default=False)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)


class Task(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"任务模组名", max_length=127)
    creator = models.ForeignKey(verbose_name=u"创作者", to=User, related_name='task_creator', on_delete=models.CASCADE)
    init_file = models.FileField(verbose_name=u"任务模组文件", upload_to="static/resource/game/tasks/")
    private = models.BooleanField(verbose_name=u"是否公开", default=False)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)


class TaskRecord(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    room = models.ForeignKey(verbose_name=u"房间", to=Room, related_name="tesk_belong_room", on_delete=models.CASCADE)
    task = models.ForeignKey(verbose_name=u"任务", to=Task, related_name="task", on_delete=models.CASCADE)
    done = models.BooleanField(verbose_name=u"是否完成", default=False)
    file = models.FileField(verbose_name=u"日志记录", upload_to="static/resource/game/records/", null=True)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)
    update_time = models.DateTimeField(verbose_name=u"更新时间", default=datetime.now)


class Item(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"物品名称", max_length=127)
    description = models.CharField(verbose_name=u"物品描述", max_length=256, null=True, blank=True)
    creator = models.ForeignKey(verbose_name=u"创作者", to=User, related_name='item_creator', on_delete=models.CASCADE)
    file = models.FileField(verbose_name=u"物品资料文件", upload_to="static/resource/game/items/", null=True, blank=True)
    private = models.BooleanField(verbose_name=u"是否公开", default=False)
    unique = models.BooleanField(verbose_name=u"是否唯一", default=False)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)


class RoomItemRecord(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    room = models.ForeignKey(verbose_name=u"房间", to=Room, on_delete=models.CASCADE)
    item = models.ForeignKey(verbose_name=u"物品", to=Item, on_delete=models.CASCADE)
    player = models.ForeignKey(verbose_name=u"玩家", to=Character, on_delete=models.CASCADE)
    private = models.BooleanField(verbose_name=u"是否公开", default=False)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)


class GameTxt(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    room_id = models.CharField(verbose_name=u"游戏房间", max_length=64, unique=True)
    user = models.ForeignKey(verbose_name=u"上传者", to=User, related_name="text_uploader", on_delete=models.CASCADE)
    file = models.FileField(verbose_name=u"游戏记录文件", max_length=512)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    class Meta:
        verbose_name = u"游戏文本信息"
        verbose_name_plural = verbose_name


# 临时文本记录器
class GameTxtPhantom:
    txt_dict = {}

    def get_by_state(self, state):
        if not self.txt_dict.get(state):
            self.txt_dict[state] = []
        return self.txt_dict.get(state)


class CharacterTxt:

    def __init__(self, name, content, time):
        self.name = name
        self.content = content
        self.time = time

    def __str__(self):
        return self.name + "(" + str(self.time) + ")" + ":" + self.content
