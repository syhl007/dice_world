import json
import random
import uuid
import time

from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models

from user_manager.models import User


def create_id():
    return "".join(random.sample(uuid.uuid4().hex, 3)) + str(int(time.time())) + "".join(
        random.sample(uuid.uuid4().hex, 3))


def create_uuid(key=None):
    if key is None:
        key = str(time.time())
    return uuid.uuid5(uuid.NAMESPACE_DNS, name=key).hex


class JSONField(models.Field):
    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid JSON."),
    }
    description = "field to store json obj(list/dict)"

    def __init__(self, verbose_name=None, **kwargs):
        super().__init__(verbose_name, **kwargs)

    '''
     用于生成数据库sql语句时指定字段类型
     ·同理，在进行数据库检索时也会以此为字段类型
     ·因为其他时候都不会被调用，所以可以进行复杂逻辑设置
     ·若返回None，则会让SQL语句生成器忽略这个字段
     ·rel_db_type与这个类似，只是是用于外键连接时说明字段类型
    '''

    def db_type(self, connection):
        return 'longtext'

    '''
     每次从数据库读取数据时，都会调用这个函数（但是不会调用to_python()）
      ·包括统计和values()函数
      ·json字段就是string转对象
      ·因为和to_python处理数据逻辑一致，可以通过to_python来实现
    '''

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)

    '''
     反序列化时调用，forms clean()时调用
      ·clean()方法是用于验证反序列化值并返回正确值
      ·对一切异常均需要抛出ValidationError
    '''

    def to_python(self, value):
        if value is not None and isinstance(value, str):
            try:
                value = value.replace("'", '"')
                return json.loads(value)
            except Exception as e:
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
        else:
            return value

    '''
     针对某些需要准备的字段调用的方法
     ·比如date时间等
     ·默认的父类方法是直接调用get_prep_value()
     ·用于保存时需要特殊转换的字段
    '''

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if not isinstance(value, str):
            return json.dumps(value)
        else:
            return value

    '''
     Python值转数据库字段存储值
     ·请返回数据库支持的字段类型，如string
    '''

    def get_prep_value(self, value):
        if not isinstance(value, str):
            return json.dumps(value)
        else:
            return value

    '''
     存储前预处理数值，如DateField中的auto_now属性等
    '''
    # def pre_save(self, model_instance, add):
    #     pass

    '''
    应该是用于关联前端页面form字段
    '''
    # def formfield(self, **kwargs):
    #     defaults = {'form_class': MyFormField}
    #     defaults.update(kwargs)
    #     return super().formfield(**defaults)


class Room(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    num = models.CharField(verbose_name=u"房间号", max_length=64, unique=True, null=False, default=create_id)
    name = models.CharField(verbose_name=u"房间名", max_length=64, default=time.time)
    gm = models.ForeignKey(verbose_name=u"GM", to=User, related_name="gm", on_delete=models.CASCADE)
    tag = JSONField(verbose_name=u"标签", null=True, blank=True)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    def __str__(self):
        return '[' + self.num + ']' + self.name

    class Meta:
        verbose_name = u"房间"
        verbose_name_plural = verbose_name


class Group(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    users = models.ManyToManyField(verbose_name=u"玩家列表", to=User, through='GroupMember')
    room = models.ForeignKey(verbose_name=u"所属房间", to=Room, related_name="room", on_delete=models.CASCADE)
    # 0——旁观者
    # 1——游戏参与者
    type = models.SmallIntegerField(verbose_name=u"队伍类型", default=0)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队"
        verbose_name_plural = verbose_name


class Character(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    name = models.CharField(verbose_name=u"角色姓名", max_length=64, null=False, blank=True)
    sex = models.SmallIntegerField(verbose_name=u"角色性别", default=0)
    head = models.ImageField(verbose_name=u"角色头像", default="templates/character/default/no_img.jpg")
    detail = models.FileField(verbose_name=u"角色资料文件")
    creator = models.ForeignKey(verbose_name=u"创作者", to=User, related_name='creator', on_delete=models.CASCADE)
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)
    editor = models.ForeignKey(verbose_name=u"修改者", to=User, related_name='editor', on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name=u"更新时间", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"游戏角色"
        verbose_name_plural = verbose_name


class GroupMember(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    user = models.ForeignKey(verbose_name=u"用户", to=User, related_name="user", on_delete=models.CASCADE)
    group = models.ForeignKey(verbose_name=u"团队", to=Group, related_name="group", on_delete=models.CASCADE)
    character = models.ForeignKey(verbose_name=u"角色", to=Character, related_name="character", null=True,
                                  on_delete=models.CASCADE)
    is_leader = models.BooleanField(verbose_name=u"队长", default=False)
    send_msg = models.BooleanField(verbose_name=u"允许发言", default=True)
    is_gamer = models.BooleanField(verbose_name=u"玩家", default=True)
    tag = models.CharField(verbose_name=u"标签", max_length=127)
    add_time = models.DateTimeField(verbose_name=u"加入时间", default=datetime.now)

    class Meta:
        verbose_name = u"团队信息"
        verbose_name_plural = verbose_name


class GameTxt(models.Model):
    id = models.UUIDField(verbose_name="UUID", max_length=64, primary_key=True, default=create_uuid)
    user = models.ForeignKey(verbose_name=u"上传者", to=User, related_name="user+", on_delete=models.CASCADE)
    file = models.FileField(verbose_name=u"游戏记录文件")
    add_time = models.DateTimeField(verbose_name=u"创建时间", default=datetime.now)

    class Meta:
        verbose_name = u"游戏文本信息"
        verbose_name_plural = verbose_name

