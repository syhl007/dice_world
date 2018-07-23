import json
import os
import random
import time
from datetime import datetime
from xml.etree import ElementTree as ET

from django import forms
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views import generic

from dice_world.settings import BASE_DIR
from dice_world.standard import JsonResponse, txt_board_storeroom
from dice_world.utils import WordFilter, DiceFilter
from game_manager.controlor import xml_file_check
from game_manager.models import Character, Room, Group, GroupMember, GameTxt, GameTxtPhantom, CharacterTxt, Task, \
    TaskRecord, Item, RoomItemRecord, Skill, RoomSkillRecord
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
    template_name = 'room/room_create.html'  # 当request以GET请求时返回的页面

    def get(self, request, *args, **kwargs):
        obj = super().get(request, *args, **kwargs)
        return obj

    def form_valid(self, form):
        with transaction.atomic():
            if form.data.get('password'):
                form.instance.password = form.data.get('password')
            form.instance.gm = self.request.user
            form.instance.sidelines = form.data.get('sidelines') == 'on'
            form.save()
            room = Room.objects.get(id=form.instance.id)
            game_players = Group.objects.create(room=room, type=0)
            GroupMember.objects.create(group=game_players, user=room.gm)
            if form.data.get('sidelines'):
                bystanders = Group()
                bystanders.room = room
                bystanders.type = 1
                if form.data.get('sidelines_sendmsg'):
                    bystanders.send_msg = False
                bystanders.save()
            if not form.data.get('password'):
                Group.objects.create(room=room, type=2)
            dir_path = "static/resource/txt/" + room.gm.username
            os.makedirs(dir_path, exist_ok=True)
            txt_path = os.path.join(dir_path, "[" + str(int(time.time())) + "]" + room.id.hex + ".txt")
            with open(txt_path, 'w') as txt:
                pass
            GameTxt.objects.create(room_id=str(room.id), user=room.gm, file=txt_path)
            txt_board_storeroom[room.id] = GameTxtPhantom()
            return JsonResponse(0, data={'room_id': str(room.id)})

    # def form_invalid(self, form):
    #     print("[form_invalid]", form.instance)
    #     pass


class JoinRoom(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        try:
            group = Group.objects.get(Q(users=request.user) & Q(room=room))
            if group.type == 2:
                return JsonResponse(state=2, msg="申请尚未通过")
            else:
                return JsonResponse(state=0, data={'group_id': str(group.id)})
        except Exception as e:
            pass
        if room.password:
            password = request.POST.get('password')
            if not password:
                return JsonResponse(state=2, msg="请输入密码")
            if password != room.password:
                return JsonResponse(state=2, msg="密码错误")
            if room.state == 1 and room.sidelines:
                group = Group.objects.get(Q(room=room) & Q(type=1))
                GroupMember.objects.create(user=request.user, group=group)
                return JsonResponse(state=0, data={'group_id': str(group.id)})
            elif room.state == 0:
                group = Group.objects.get(Q(room=room) & Q(type=0))
                GroupMember.objects.create(user=request.user, group=group)
                return JsonResponse(state=0, data={'group_id': str(group.id)})
            elif room.state == -1:
                return JsonResponse(state=2, msg="已结团")
            else:
                return JsonResponse(state=2, msg="加入房间失败")
        else:
            if room.sidelines:
                group = Group.objects.get(Q(room=room) & Q(type=2))
                GroupMember.objects.create(user=request.user, group=group)
                return JsonResponse(state=2, msg="已提交申请")
            elif room.state == 1 and not room.sidelines:
                return JsonResponse(state=2, msg="跑团中，禁止旁观")
            elif room.state == -1:
                return JsonResponse(state=2, msg="已结团")
            else:
                return JsonResponse(state=2, msg="加入房间失败")


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        context['is_gm'] = (request.user == self.object.gm)
        context['room_id'] = kwargs['pk']
        GroupMember.objects.filter(Q(user=request.user) & Q(group__room=self.object)).update(is_online=True)
        return self.render_to_response(context)


class ListGroup(generic.View):
    template_name = 'room/group_label.html'

    def get(self, request, *args, **kwargs):
        groups = Group.objects.filter(room__id=kwargs['room_id']).order_by('type')
        groups_list = []
        length = 0
        for g in groups:
            groups_list.append({'id': g.id, 'type': g.type, 'send_msg': g.send_msg})
            length += 1
        context = {'groups': groups_list, 'group_length': length, 'room_id': kwargs['room_id']}
        return TemplateResponse(
            request=request,
            template=self.template_name,
            context=context, )


class ListPlayer(generic.View):

    def get(self, request, *args, **kwargs):
        characters = Character.objects.only('id', 'name').filter(group_character__group__room_id=kwargs['room_id'])
        characters_list = []
        for character in characters:
            characters_list.append({'id': character.id.hex, 'name': character.name})
        return JsonResponse(state=0, data=characters_list)


class ManageGroup(generic.View):

    def post(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=2, msg="权限不足")
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
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if game_txt_phantom:
            txt_list = [str(txt) for txt in game_txt_phantom.get_by_state(state) if
                        not time_line or txt.time > time_line]
            if txt_list:
                return JsonResponse(state=0, data={'time_line': str(datetime.now()), 'list': txt_list})
            else:
                return JsonResponse(state=3, msg="没有新的消息")
        else:
            return JsonResponse(state=3, msg="没有消息记录")

    def post(self, request, *args, **kwargs):
        user = request.user
        room_id = kwargs['room_id']
        try:
            room = Room.objects.get(id=room_id)
            group = Group.objects.filter(room=room).get(users=user)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned, Room.DoesNotExist, Room.MultipleObjectsReturned):
            return JsonResponse(state=2, msg="群组或房间异常")
        if not group.send_msg:
            return JsonResponse(state=2, msg="群组禁言中")
        text = request.POST.get('text')
        state = request.POST.get('state')
        if not text:
            return JsonResponse(state=1, msg="空白信息")
        if state == 'game':
            try:
                group_member = GroupMember.objects.filter(group=group).get(user=user)
                if not group_member.send_msg:
                    return JsonResponse(state=2, msg="角色被禁言")
                character = group_member.character
                name = character.name
            except Exception as e:
                # print(e)
                # return JsonResponse(state=1, msg="游戏角色获取异常"))
                name = '神秘声音'
        else:
            name = user.username
        if text.startswith('.'):
            text = DiceFilter.handle(text)
        text = WordFilter.handle(text)
        t = datetime.now()
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if not game_txt_phantom:
            game_txt_phantom = GameTxtPhantom()
            txt_board_storeroom[room_id] = game_txt_phantom
        game_txt_phantom.get_by_state(state).append(CharacterTxt(name=name, content=text, time=t))
        return JsonResponse(state=0)


class StartGame(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg='不是房主权限')
        room.state = 1
        room.save()
        t = datetime.now()
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if not game_txt_phantom:
            game_txt_phantom = GameTxtPhantom()
            txt_board_storeroom[room_id] = game_txt_phantom
        game_txt_phantom.get_by_state('game').append(CharacterTxt(name='GM',
                                                                  content='\n-------------------------\n游戏开始：' + str(
                                                                      datetime.now()) + '\n-------------------------\n',
                                                                  time=datetime.now()))
        Group.objects.filter(Q(room=room) & Q(users=request.user)).update(send_msg=True)
        return JsonResponse(state=0)


class SaveRoomChat(generic.View):

    def post(self, request, *args, **kwargs):
        user = request.user
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.gm != user:
            return JsonResponse(state=2, msg='不具有权限')
        room.state = 0
        room.save()
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if game_txt_phantom:
            game_txt_phantom.get_by_state('game').append(CharacterTxt(name='GM',
                                                                      content='\n-------------------------\n存盘时间：' + str(
                                                                          datetime.now()) + '\n-------------------------\n',
                                                                      time=datetime.now()))
            Group.objects.filter(Q(room=room) & Q(users=user)).update(send_msg=False)
            txt_list = [str(txt) for txt in game_txt_phantom.get_by_state('game')]
            if txt_list:
                game_txt = GameTxt.objects.filter(user=request.user).get(room_id=room_id)
                with open(game_txt.file.path, 'a') as f:
                    for t in txt_list:
                        f.write(t)
                        f.write('\n')
                game_txt_phantom.clear_by_state('game')
                Group.objects.filter(Q(room=room) & Q(users=user)).update(send_msg=False)
                return JsonResponse(state=0)
            else:
                return JsonResponse(state=2, msg="没有消息记录")
        else:
            return JsonResponse(state=2, msg="没有消息记录")


class EndGame(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg="不具有房主权限")
        game_txt_phantom = txt_board_storeroom.get(room_id)
        if game_txt_phantom:
            game_txt_phantom.get_by_state('game').append(CharacterTxt(name='GM',
                                                                      content='\n-------------------------\n结团时间：' + str(
                                                                          datetime.now()) + '\n-------------------------\n',
                                                                      time=datetime.now()))
            Group.objects.filter(room=room).update(send_msg=False)
            txt_list = [str(txt) for txt in game_txt_phantom.get_by_state('game')]
            if txt_list:
                game_txt = GameTxt.objects.filter(user=request.user).get(room_id=room_id)
                with open(game_txt.file.path, 'a') as f:
                    for t in txt_list:
                        f.write(t)
                        f.write('\n')
        txt_board_storeroom['room_id'] = None
        record_dict = {}
        record_dict['游戏文本'] = str(GameTxt.objects.get(room_id=room_id).file)
        for task_record in TaskRecord.objects.select_related('task').filter(room_id=room_id):
            record_dict[task_record.task.name] = str(task_record.file)
        room.state = -1
        room.save()
        return JsonResponse(state=0, data=record_dict)


class ListTask(generic.ListView):
    template_name = 'room/dialog_task_list.html'

    def get(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg="不具有房主权限")
        self.queryset = Task.objects.filter(Q(room_task__id=room_id))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        task_before_list = TaskRecord.objects.filter(room_id=room_id)
        context['task_before_list'] = task_before_list
        task_after_list = Task.objects.filter(Q(creator=request.user) | Q(private=False))
        context['task_after_list'] = task_after_list
        context['is_gm'] = True
        context['room_id'] = kwargs['room_id']
        return self.render_to_response(context)


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
        dir_path = "static/resource/game/records/"
        os.makedirs(dir_path, exist_ok=True)
        txt_path = os.path.join(dir_path, "[" + str(int(time.time())) + "]" + form.instance.id + ".txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(str(datetime.now())+':'+'\n')
            f.write(start)
            f.write('\n')
        form.instance.file = txt_path
        form.save()
        return JsonResponse(state=0)


class RecordTask(generic.View):

    def post(self, request, *args, **kwargs):
        task_record_id = request.POST['task_record_id']
        task_record = TaskRecord.objects.get(id=task_record_id)
        task_record.update_time = datetime.now()
        task_record.save()
        record = request.POST.get('record')
        with open(task_record.file.path, 'a', encoding='utf-8') as f:
            f.write(str(datetime.now()) + ':' + '\n')
            f.write(record)
            f.write('\n')
        return JsonResponse(state=0)


class ListItem(generic.ListView):
    template_name = 'room/dialog_item_list.html'

    def get(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm == request.user:
            self.queryset = RoomItemRecord.objects.select_related('player').select_related('item').filter(
                room_id=kwargs['room_id'])
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            item_before_list = Item.objects.filter(room_item__id=kwargs['room_id'])
            context['item_before_list'] = item_before_list
            item_after_list = Item.objects.filter(Q(creator=request.user) | Q(private=False))
            context['item_after_list'] = item_after_list
            context['is_gm'] = True
        else:
            self.queryset = RoomItemRecord.objects.filter(Q(room_id=kwargs['room_id']) | Q(
                player__group_character__user=request.user))
            self.object_list = self.get_queryset()
            context = self.get_context_data()
        context['room_id'] = kwargs['room_id']
        return self.render_to_response(context)


class ItemGet(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        player_ids = request.POST.getlist('player_ids')
        item_id = request.POST['item_id']
        item = Item.objects.get(id=item_id)
        if item.unique:
            if len(player_ids) > 1:
                return JsonResponse(state=2, msg='唯一物品不能赋予两个以上角色')
            try:
                RoomItemRecord.objects.get(Q(room_id=room_id) & Q(item_id=item_id))
                return JsonResponse(state=2, msg='已存在该唯一物品')
            except RoomItemRecord.MultipleObjectsReturned:
                return JsonResponse(state=2, msg='多于两个唯一物品')
            except RoomItemRecord.DoesNotExist:
                pass
        item_record_list = [RoomItemRecord(player_id=player_id, room_id=room_id, item_id=item_id) for player_id in
                            player_ids]
        RoomItemRecord.objects.bulk_create(item_record_list)
        return JsonResponse(state=0)


class ItemLost(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        item_id = request.POST['item_id']
        if room.gm == request.user:
            player_id = request.POST['player_id']
            RoomItemRecord.objects.filter(player_id=player_id, room_id=room_id, item_id=item_id).delete()
        else:
            RoomItemRecord.objects.filter(player__group_character__user=request.user, room_id=room_id,
                                          item_id=item_id).delete()
        return JsonResponse(state=0)


class ItemChange(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        player_ids = request.POST.getlist('player_ids')
        if len(player_ids) > 1:
            return JsonResponse(state=2, msg="不能转交给多个玩家")
        player_id = player_ids[0]
        item_id = request.POST['item_id']
        if room.gm == request.user:
            owner_id = request.POST['owner_id']
            RoomItemRecord.objects.filter(player_id=owner_id, room_id=room_id, item_id=item_id).update(
                player_id=player_id)
        else:
            RoomItemRecord.objects.filter(player__group_character__user=request.user, room_id=room_id,
                                          item_id=item_id).update(player_id=player_id)
        return JsonResponse(state=0)


class ItemAdd(generic.View):

    def post(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=2, msg='没有房主权限')
        room.items.add(Item.objects.get(id=request.POST.get('item_id')))
        return JsonResponse(state=0)


class ListSkill(generic.ListView):
    template_name = 'room/dialog_skill_list.html'

    def get(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm == request.user:
            self.queryset = RoomSkillRecord.objects.select_related('player').select_related('skill').filter(
                room_id=kwargs['room_id'])
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            skill_before_list = Skill.objects.filter(room_skill__id=kwargs['room_id'])
            context['skill_before_list'] = skill_before_list
            skill_after_list = Skill.objects.filter(Q(creator=request.user) | Q(private=False))
            context['skill_after_list'] = skill_after_list
            context['is_gm'] = True
        else:
            self.queryset = RoomSkillRecord.objects.filter(Q(room_id=kwargs['room_id']) | Q(
                player__group_character__user=request.user))
            self.object_list = self.get_queryset()
            context = self.get_context_data()
        context['room_id'] = kwargs['room_id']
        return self.render_to_response(context)


class SkillGet(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        player_ids = request.POST.getlist('player_ids')
        skill_id = request.POST['skill_id']
        skill = Skill.objects.get(id=skill_id)
        if skill.unique:
            if len(player_ids) > 1:
                return JsonResponse(state=2, msg='独有技能不能赋予两个以上角色')
            try:
                RoomSkillRecord.objects.get(Q(room_id=room_id) & Q(skill_id=skill_id))
                return JsonResponse(state=2, msg='已存在该独有技能')
            except RoomSkillRecord.MultipleObjectsReturned:
                return JsonResponse(state=2, msg='多于两个独有技能')
            except RoomSkillRecord.DoesNotExist:
                pass
        skill_record_list = [RoomSkillRecord(player_id=player_id, room_id=room_id, skill=skill) for player_id in
                             player_ids]
        RoomSkillRecord.objects.bulk_create(skill_record_list)
        return JsonResponse(state=0)


class SkillLost(generic.View):

    def post(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        room = Room.objects.get(id=room_id)
        skill_id = request.POST['skill_id']
        if room.gm == request.user:
            player_id = request.POST['player_id']
            RoomSkillRecord.objects.filter(player_id=player_id, room_id=room_id, skill_id=skill_id).delete()
        else:
            RoomSkillRecord.objects.filter(player__group_character__user=request.user, room_id=room_id,
                                           skill_id=skill_id).delete()
        return JsonResponse(state=0)


class SkillAdd(generic.View):

    def post(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=2, msg='没有房主权限')
        room.skills.add(Skill.objects.get(id=request.POST.get('skill_id')))
        return JsonResponse(state=0)


class TaskAdd(generic.View):

    def post(self, request, *args, **kwargs):
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=2, msg='没有房主权限')
        task_id = request.POST.get('task_id')
        task = Task.objects.get(id=task_id)
        room.tasks.add(task)
        return JsonResponse(state=0)


class TaskRecordDetail(generic.View):

    def get(self, request, *args, **kwargs):
        task_record_id = kwargs['task_record_id']
        room = Room.objects.get(id=kwargs['room_id'])
        if room.gm != request.user:
            return JsonResponse(state=2, msg='不具有房主权限')
        task_record = TaskRecord.objects.select_related('room', 'task').get(id=task_record_id)
        with open(task_record.file.path, 'r', encoding='utf-8') as f:
            task_record_txt = f.readlines()
        return render(request, 'room/executing_task_detail.html',
                      context={'task_record': task_record, 'task_record_txt': task_record_txt})
