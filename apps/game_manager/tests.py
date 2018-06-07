import json
import random
import time
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

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
        # print("[11]", type(test_room_1.id), test_room_1.id)
        # print("[str_uuid]", str_uuid)
        # print("[22]", type(test_room_2.id), test_room_2.id)
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
        time.sleep(1)
        print('_________')
        queryset = Room.objects.all().order_by("add_time")
        room_1 = queryset[0]
        room_2 = queryset[1]
        room_3 = queryset[2]
        room_4 = queryset[3]
        # print(room_1.tag)
        # print(room_2.tag)
        # print(room_3.tag)
        # print(room_4.tag)
        self.assertIs(isinstance(room_1.tag, dict), True)
        self.assertIs(isinstance(room_2.tag, dict), True)
        self.assertIs(isinstance(room_3.tag, list), True)
        self.assertIs(isinstance(room_4.tag, list), True)


# 房间列表视图测试
class RoomViewTest(TestCase):
    def test_html_ready(self):
        response = self.client.get(reverse('room:room_list'))
        self.assertContains(response, 'No room are available.')
        User.objects.create(username="atman")
        user = User.objects.all()[0]
        Room.objects.create(name="auto_test_001", gm=user)
        time.sleep(1)
        Room.objects.create(name="auto_test_002", gm=user)
        time.sleep(1)
        Room.objects.create(name="auto_test_003", gm=user)
        response = self.client.get(reverse('room:room_list'))
        self.assertIs(response.status_code == 200, True)
        self.assertIs(len(response.context['room_list']) == Room.objects.all().count(), True)
        print(response.context['room_list'])
        index = random.randint(0, len(response.context['room_list']) - 2)
        room_a = response.context['room_list'][index]
        room_b = response.context['room_list'][index + 1]
        self.assertIs(room_b.add_time <= room_a.add_time, True)

    def test_post_filter(self):
        User.objects.create()
        user = User.objects.all()[0]
        Room.objects.create(name="asd", gm=user, tag=['测试', '无效'])
        time.sleep(1)
        Room.objects.create(name=123, gm=user, tag=['实际', '无效'])
        response = self.client.get(reverse('room:room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['room_list']), 2)
        # print("[get]", response.context['room_list'])
        response = self.client.post(reverse('room:room_list'), data={"filter": '{"name": 123}'})
        # print("[post1]", response.context['room_list'])
        self.assertEqual(response.context['room_list'][0].name, '123')
        # response = self.client.post(reverse('room:room_list'), data={"filter": '{"tag__contains": "实际"}'})
        # print("[post2]", response.context['room_list'])
        # self.assertEqual(response.context['room_list'][0].name, '123')

    def test_create_room(self):
        g_resp = self.client.get(reverse('room:room_create'), data={'name': 'test'})
        print("[get]", g_resp.content)
        User.objects.create()
        user = User.objects.all()[0]
        response = self.client.get(reverse('room:room_list'))
        print(response.context['room_list'])
        p_resp = self.client.post(reverse('room:room_create'), data={'name': 'test', 'gm': user})
        print("[post]", str(p_resp.content))
        response = self.client.get(reverse('room:room_list'))
        print("[room_list]", response.context['room_list'])
        self.assertIs(len(response.context['room_list']) == Room.objects.all().count(), True)


