import json
import random

import time
import uuid

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponse

txt_board_storeroom = {}

global_websocket_dict = {}


def create_uuid(key=None):
    if key is None:
        key = str(time.time())
    return uuid.uuid5(uuid.NAMESPACE_DNS, name=key).hex


def create_id():
    return "".join(random.sample(uuid.uuid4().hex, 3)) + str(int(time.time())) + "".join(
        random.sample(uuid.uuid4().hex, 3))


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
        value = value.strip();
        if value and isinstance(value, str):
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


class JsonResponse(HttpResponse):
    '''
        {'state':0,'msg':'xxxx', 'data': 'JsonObj'}
    '''

    def __init__(self, state, msg=None, data=None):
        super().__init__()
        self.state = state
        self.msg = str(msg)
        self.data = data
        self.content = self.__str__()

    def __str__(self):
        res = {}
        res['state'] = self.state
        if self.msg:
            res['msg'] = self.msg
        if self.data:
            res['data'] = json.dumps(self.data)
        return json.dumps(res)
