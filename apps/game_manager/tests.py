import uuid

import time
from django.db import IntegrityError
from django.test import TestCase

from game_manager.models import Room
from user_manager.models import User


# 房间类测试
class RoomModelTest(TestCase):

    # 房间名不能重复
    def test_room_num_unique(self):
        User.objects.create()
        user = User.objects.all()[0]
        Room.objects.create(gm=user)
        test_room = Room.objects.all()[0]
        try:
            Room.objects.create(gm=user, num=test_room.num)
        except Exception as e:
            self.assertIs(isinstance(e, IntegrityError), True)

    # 通过string类型的uuid获取房间类
    def test_get_room_by_str_uuid(self):
        user = User()
        user.save()
        Room.objects.create(gm=user)
        test_room_1 = Room.objects.all()[0]
        str_uuid = str(test_room_1.id)
        test_room_2 = Room.objects.get(id=str_uuid)
        self.assertIs(test_room_1.num == test_room_2.num, True)
        self.assertIs(test_room_1.add_time == test_room_2.add_time, True)
        print("[11]", type(test_room_1.id), test_room_1.id)
        print("[str_uuid]", str_uuid)
        print("[22]", type(test_room_2.id), test_room_2.id)
        self.assertIs(test_room_1.id == test_room_2.id, True)
        self.assertIs(test_room_1 == test_room_2, True)

    # JSONField测试
    def test_json_field(self):
        User.objects.create()
        user = User.objects.all()[0]
        str_test_1 = '{"a": 1, "b":"test"}'
        dict_test = {'c': 2, 'd': 'test'}
        str_test_2 = '["a","b",2,5,2.5,"2.5"]'
        list_test = ["c", "d", 1, 3, 1.3, "1.3"]
        Room.objects.create(gm=user, tag=str_test_1)
        time.sleep(1)
        Room.objects.create(gm=user, tag=dict_test)
        time.sleep(1)
        Room.objects.create(gm=user, tag=str_test_2)
        time.sleep(1)
        Room.objects.create(gm=user, tag=list_test)
        print('_________')
        room_1 = Room.objects.all()[0]
        room_2 = Room.objects.all()[1]
        room_3 = Room.objects.all()[2]
        room_4 = Room.objects.all()[3]
        print(room_1.tag)
        print(room_2.tag)
        print(room_3.tag)
        print(room_4.tag)
        self.assertIs(isinstance(room_1.tag, dict), True)
        self.assertIs(isinstance(room_2.tag, dict), True)
        self.assertIs(isinstance(room_3.tag, list), True)
        self.assertIs(isinstance(room_4.tag, list), True)
