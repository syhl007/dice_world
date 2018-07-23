from django import forms
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.views import generic
from xml.etree import ElementTree as ET

from dice_world.standard import JsonResponse
from game_manager.controlor import xml_file_check
from game_manager.models import Character, Group, GroupMember, Room, Task


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
            xml_file_check(form.instance.detail)
            return JsonResponse(state=0)

    def form_invalid(self, form):
        return JsonResponse(state=2, msg='数据异常，请检查输入数据。')


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
            return JsonResponse(state=2, msg='文件不符合模板错误')
        for i in r:
            text = i.text.replace(i.tail, '')
            text = text.replace('\t', '')
            character_info[i.tag] = text
        return render(request, 'character/character_detail.html',
                      context={'character': character, 'character_info': character_info})


class ListCharacter(generic.ListView):
    template_name = 'character/character_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Character.objects.filter(Q(creator=request.user) | Q(private=False))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if kwargs.get('group_id'):
            context['group_id'] = kwargs['group_id']
        if kwargs.get('room_id'):
            room = Room.objects.get(id=kwargs['room_id'])
            if room.gm == request.user:
                character_before_list = Character.objects.filter(room_npc__id=kwargs['room_id'])
                context['character_before_list'] = character_before_list
        return self.render_to_response(context)


class LinkCharacter(generic.View):

    def post(self, request, *args, **kwargs):
        user = request.user
        group = Group.objects.get(id=request.POST.get('group_id'))
        character = Character.objects.get(id=request.POST.get('character_id'))
        GroupMember.objects.filter(group=group).filter(user=user).update(character=character)
        return JsonResponse(state=0)


class ListNPC(generic.ListView):
    template_name = 'character/task_npc_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Character.objects.filter(Q(creator=request.user) | Q(private=False))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['task_id'] = kwargs['task_id']
        return self.render_to_response(context)


class AddNPC(generic.View):

    def post(self, request, *args, **kwargs):
        character = Character.objects.get(id=request.POST['character_id'])
        task = Task.objects.get(id=request.POST['task_id'])
        task.npc.add(character)
        return JsonResponse(state=0, msg='添加成功')



