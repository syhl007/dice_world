import json
import os
import random
import time
from datetime import datetime
from xml.etree import ElementTree as ET

from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views import generic

from dice_world.settings import BASE_DIR
from dice_world.standard import JsonResponse, txt_board_storeroom
from dice_world.utils import WordFilter, DiceFilter
from game_manager.models import Character, Room, Group, GroupMember, GameTxt, GameTxtPhantom, CharacterTxt, Task, \
    TaskRecord, Item
from user_manager.models import User


class ListRoom(generic.ListView):
    model = Room
    template_name = 'room/room_list.html'
    ordering = '-add_time'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        filter = request.POST.get('filter')
        print("[filter]", filter)
        if filter is not None:
            filter = json.loads(filter)
            print("[filter_loads]", filter)
        self.queryset = Room.objects.filter(**filter)
        context = self.get_context_data()
        response = self.render_to_response(context)
        return response


class CreateRoom(generic.CreateView):
    model = Room  # 生成的模型对象类、不设置这个的话就会去检测self.object和self.queryset来确定
    fields = ['name', 'background', ]  # 需要获取的字段，必须
    template_name = 'room/create_room.html'  # 当request以GET请求时返回的页面

    def get(self, request, *args, **kwargs):
        obj = super().get(request, *args, **kwargs)
        return obj

    def form_valid(self, form):
        with transaction.atomic():
            if form.data.get('password'):
                form.instance.password = form.data.get('password')
            form.instance.gm = self.request.user
            form.save()
            room = Room.objects.get(id=form.instance.id)
            game_players = Group.objects.create(room=room, type=0)
            GroupMember.objects.create(group=game_players, user=room.gm)
            if form.data.get('sidelines_allowed'):
                bystanders = Group()
                bystanders.room = room
                bystanders.type = 1
                if form.data.get('sidelines_sendmsg'):
                    bystanders.send_msg = False
                bystanders.save()
            if not form.data.get('password'):
                Group.objects.create(room=room, type=2)
            dir_path = os.path.join(BASE_DIR, "txt/" + room.gm.username)
            os.makedirs(dir_path, exist_ok=True)
            txt_path = os.path.join(dir_path, "[" + room.id.hex + "-" + room.name + "]" + str(time.time()) + ".txt")
            with open(txt_path, 'w') as txt:
                pass
            GameTxt.objects.create(room_id=str(room.id), user=room.gm, file=txt_path)
            txt_board_storeroom[room.id] = GameTxtPhantom()
            return JsonResponse(0, data={'room_id': str(room.id)})

    # def form_invalid(self, form):
    #     print("[form_invalid]", form.instance)
    #     pass


class JoinRoom(generic.View):

    def get(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.state == -1:
            return JsonResponse(state=1, msg="游戏已结束")
        elif room.state == 1 and not room.sidelines:
            return JsonResponse(state=1, msg="游戏已开始，且不允许旁观")
        elif room.password:
            return JsonResponse(state=2, msg="需要输入密码")
        else:
            return JsonResponse(state=0)

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.password:
            password = request.POST.get('password')
            if not password or password != room.password:
                return JsonResponse(state=1, msg="密码错误")
            if room.state == 1 and room.sidelines:
                group = Group.objects.get(Q(room=room) & Q(type=0))
                GroupMember.objects.create(user=request.user, group=group)
            elif room.state == 0:
                group = Group.objects.get(Q(room=room) & Q(type=1))
                GroupMember.objects.create(user=request.user, group=group)
            else:
                return JsonResponse(state=1, msg="加入房间失败")
        else:
            if room.state != -1:
                group = Group.objects.get(Q(room=room) & Q(type=2))
                GroupMember.objects.create(user=request.user, group=group)
            else:
                return JsonResponse(state=1, msg="加入房间失败")


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        room = self.object
        Group.objects.get(Q(users=request.user) & Q(room=room)).group.filter(user=request.user).update(is_online=True)
        return response


class ListCharacter(generic.ListView):
    model = Character
    context_object_name = 'character_list'
    template_name = 'character/character_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Character.objects.filter(Q(creator=request.user) | Q(private=False))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if kwargs.get('group_id'):
            context['group_id'] = kwargs['group_id']
        return self.render_to_response(context)


class LinkCharacter(generic.View):

    def post(self, request, *args, **kwargs):
        user = request.user
        group = Group.objects.get(id=request.POST.get('group_id'))
        character = Character.objects.get(id=request.POST.get('character_id'))
        GroupMember.objects.filter(group=group).filter(user=user).update(character=character)
        return JsonResponse(state=0)


class ListGroup(generic.View):
    template_name = 'room/group_label.html'

    def get(self, request, *args, **kwargs):
        groups = Group.objects.filter(room__id=kwargs['room_id']).order_by('type')
        groups_list = []
        for g in groups:
            groups_list.append({'id': g.id, 'type': g.type, 'send_msg': g.send_msg})
        context = {'groups': groups_list, 'room_id': kwargs['room_id']}
        return TemplateResponse(
            request=request,
            template=self.template_name,
            context=context, )


class ListGroupCharacter(generic.ListView):
    queryset = GroupMember
    template_name = 'room/player_character_list.html'

    def get(self, request, *args, **kwargs):
        group = Group.objects.get(id=kwargs["group_id"])
        self.queryset = GroupMember.objects.select_related('user', 'character').filter(group=group).order_by(
            '-is_online')
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['group_id'] = group.id
        context['user_id'] = request.user.id
        return self.render_to_response(context)


class ManageGroup(generic.View):

    def post(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=1, msg="权限不足")
        operation = request.POST.get('operation')
        if operation == 1:
            Group.objects.filter(Q(user__id=request.POST.get('user_id')) & Q(room=room))
            pass
        pass


class RoomChat(generic.View):

    def get(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        state = request.GET.get('state')
        time_line = request.GET.get('time_line')
        if time_line:
            time_line = datetime.strptime(time_line, '%Y-%m-%d %H:%M:%S.%f')
        try:
            room = Room.objects.get(id=room_id)
        except (Room.DoesNotExist, Room.MultipleObjectsReturned):
            return JsonResponse(state=1, msg="房间id异常")
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if game_txt_phantom:
            txt_list = [str(txt) for txt in game_txt_phantom.get_by_state(state) if
                        not time_line or txt.time > time_line]
            if txt_list:
                return JsonResponse(state=0, data={'time_line': str(datetime.now()), 'list': txt_list})
            else:
                return JsonResponse(state=2, msg="没有新的消息")
        else:
            return JsonResponse(state=2, msg="没有消息记录")

    def post(self, request, *args, **kwargs):
        user = request.user
        room_id = kwargs['room_id']
        try:
            room = Room.objects.get(id=room_id)
            group = Group.objects.filter(room=room).get(users=user)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned, Room.DoesNotExist, Room.MultipleObjectsReturned):
            return JsonResponse(state=1, msg="群组或房间异常")
        if not group.send_msg:
            return JsonResponse(state=1, msg="群组禁言中")
        text = request.POST.get('text')
        state = request.POST.get('state')
        if state == 'game':
            try:
                character = GroupMember.objects.filter(group=group).get(user=user).character
                name = character.name
            except Exception as e:
                # print(e)
                # return JsonResponse(state=1, msg="游戏角色获取异常"))
                name = '神秘声音'
        else:
            name = user.username
        if text.startswith('.'):
            text_group = DiceFilter.handle(text)
            if text_group:
                if text_group.group(1):
                    dice_num = int(text_group.group(1))
                else:
                    dice_num = 1
                dice_face = 1 if int(text_group.group(2)) == 0 else int(text_group.group(2))
                if text_group.group(4):
                    reason = text_group.group(4)
                else:
                    reason = '测手气'
                dice_list = [random.randint(1, dice_face) for i in range(dice_num)]
                total = sum(dice_list)
                text = '因为【' + reason + '】骰出：' + str(dice_list) + '=' + str(total)
        text = WordFilter.handle(text)
        t = datetime.now()
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if not game_txt_phantom:
            game_txt_phantom = GameTxtPhantom()
            txt_board_storeroom[room_id] = game_txt_phantom
        game_txt_phantom.get_by_state(state).append(CharacterTxt(name=name, content=text, time=t))
        return JsonResponse(state=0)


class SaveRoomChat(generic.View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(state=2, msg="不接收get请求")

    def post(self, request, *args, **kwargs):
        user = request.user
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.gm != user:
            return JsonResponse(state=1, msg='不具有权限')
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if game_txt_phantom:
            txt_list = [str(txt) for txt in game_txt_phantom.get_by_state('game')]
            if txt_list:
                game_txt = GameTxt.objects.filter(user=request.user).get(room_id=room_id)
                with open(game_txt.file.path, 'a') as f:
                    for t in txt_list:
                        f.write(t)
                        f.write('\n')
                    f.write(
                        '\n-------------------------\n存盘时间：' + str(datetime.now()) + '\n-------------------------\n')
                txt_board_storeroom.pop(room_id)
                return JsonResponse(state=0)
            else:
                return JsonResponse(state=1, msg="没有消息记录")
        else:
            return JsonResponse(state=1, msg="没有消息记录")


class CreateCharacter(generic.CreateView):
    model = Character
    fields = ['name', 'sex', 'head', 'detail', 'private']
    template_name = 'character/character_create.html'

    def get(self, request, *args, **kwargs):
        self.object = None  # 迷
        form = self.get_form()
        form.fields['sex'] = forms.ChoiceField(choices=((0, '男'), (1, '女'), (2, '其他')), label='性别')
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        with transaction.atomic():
            if form.data.get('id'):
                form.instance.editor = self.request.user
            else:
                form.instance.creator = self.request.user
                form.instance.editor = self.request.user
            form.save()
            return JsonResponse(0)


class CharacterDetail(generic.View):

    def get(self, request, *args, **kwargs):
        character_id = kwargs['character_uuid']
        character = Character.objects.get(id=character_id)
        if character.sex == 0:
            sex = '男'
        elif character.sex == 1:
            sex = '女'
        else:
            sex = '其他'
        character_info = {'id': character.id.hex, 'name': character.name, 'sex': sex}
        character_xml = ET.parse(character.detail)
        r = character_xml.getroot()
        print(r.tag)
        if r.tag != 'character':
            return JsonResponse(state=1, msg='文件不符合模板错误')
        for i in r:
            text = i.text.replace(i.tail, '')
            text = text.replace('\t', '')
            character_info[i.tag] = text
        return render(request, 'character/character_detail.html',
                      context={'character': character, 'character_info': character_info})


class CreateTask(generic.CreateView):
    model = Task
    fields = ['name', 'init_file', 'private']
    template_name = 'game/task_create.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.save()


class ListTask(generic.ListView):
    model = Task
    template_name = 'game/task_list.html'


class StartTask(generic.CreateView):
    model = TaskRecord
    fields = []
    template_name = 'game/task_start.html'

    def form_valid(self, form):
        room_id = form.data.get('room_id')
        form.instance.room = Room.objects.get(id=room_id)
        task_id = form.data.get('task_id')
        form.instance.task = Task.objects.get(id=task_id)
        start = form.data.get('start')
        path = None
        with open(path, 'w') as f:
            f.write(start)
        form.instance.file = path
        form.save()


class CreateItem(generic.CreateView):
    model = Item
    fields = ['name', 'file', 'private']
    template_name = 'game/item_create.html'


class ListItem(generic.ListView):
    model = Item
    template_name = 'game/item_list.html'
