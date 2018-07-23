from xml.etree import ElementTree as ET

from django.db import transaction
from django.shortcuts import render
from django.views import generic

from dice_world.standard import JsonResponse
from game_manager.controlor import xml_file_check
from game_manager.models import Task, Item, Skill, TaskRecord


class CreateItem(generic.CreateView):
    model = Item
    fields = ['name', 'pic', 'file', 'private', 'unique', 'detail']
    template_name = 'game/item_create.html'

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.creator = self.request.user
            form.instance.description = form.data.get('description')
            form.save()
            xml_file_check(form.instance.file.name)
            return JsonResponse(state=0)

    def form_invalid(self, form):
        return JsonResponse(state=2, msg='数据异常，请检查输入数据。')


class ItemDetail(generic.View):

    def get(self, request, *args, **kwargs):
        item_id = kwargs['item_id']
        item = Item.objects.get(id=item_id)
        item_info = {}
        if item.file:
            character_xml = ET.parse(item.file)
            r = character_xml.getroot()
            print(r.tag)
            if r.tag != 'item':
                return JsonResponse(state=2, msg='文件不符合模板错误')
            for i in r:
                text = i.text.replace(i.tail, '')
                text = text.replace('\t', '')
                item_info[i.tag] = text
        return render(request, 'game/item_detail.html',
                      context={'item': item, 'item_info': item_info})


class CreateTask(generic.CreateView):
    model = Task
    fields = ['name', 'init_file', 'private']
    template_name = 'game/task_create.html'

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.creator = self.request.user
            form.instance.description = form.data.get('description')
            form.save()
            xml_file_check(form.instance.init_file.name)
            return JsonResponse(state=0)


class TaskDetail(generic.View):

    def get(self, request, *args, **kwargs):
        task_id = kwargs['task_id']
        task = Task.objects.get(id=task_id)
        task_record_list = []
        task_npc_list = task.npc.all()
        is_creator = False
        if task.creator == request.user:
            is_creator = True
            task_record_list = TaskRecord.objects.select_related('room', 'room__gm').only('id', 'room__name',
                                                                                          'room__gm__username').filter(
                task_id=task_id)
        return render(request, 'game/task_detail.html',
                      context={'task': task, 'task_npc_list': task_npc_list, 'task_record_list': task_record_list,
                               'is_creator': is_creator})


class TaskRecordDetail(generic.View):

    def post(self, request, *args, **kwargs):
        record = TaskRecord.objects.get(id=request.POST['record_id'])
        with open(record.file.path) as f:
            txt = f.readlines()
        return JsonResponse(state=0, data=txt)


class CreateSkill(generic.CreateView):
    model = Skill
    fields = ['name', 'pic', 'private', 'unique', 'file', 'detail']
    template_name = 'game/skill_create.html'

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.creator = self.request.user
            form.instance.description = form.data.get('description')
            form.save()
            return JsonResponse(state=0)


class SkillDetail(generic.View):

    def get(self, request, *args, **kwargs):
        skill_id = kwargs['skill_id']
        skill = Skill.objects.get(id=skill_id)
        skill_info = {}
        if skill.file:
            character_xml = ET.parse(skill.file)
            r = character_xml.getroot()
            print(r.tag)
            if r.tag != 'skill':
                return JsonResponse(state=2, msg='文件不符合模板错误')
            for i in r:
                text = i.text.replace(i.tail, '')
                text = text.replace('\t', '')
                skill_info[i.tag] = text
        return render(request, 'game/skill_detail.html', context={'skill': skill, 'skill_info': skill_info})
