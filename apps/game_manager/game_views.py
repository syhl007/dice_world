from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.views import generic
from xml.etree import ElementTree as ET

from dice_world.standard import JsonResponse
from game_manager.controlor import xml_file_check
from game_manager.models import Task, Item, Room, RoomItemRecord


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


class CreateItem(generic.CreateView):
    model = Item
    fields = ['name', 'pic', 'file', 'private', 'unique']
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
        character_xml = ET.parse(item.file)
        r = character_xml.getroot()
        print(r.tag)
        if r.tag != 'item':
            return JsonResponse(state=1, msg='文件不符合模板错误')
        for i in r:
            text = i.text.replace(i.tail, '')
            text = text.replace('\t', '')
            item_info[i.tag] = text
        return render(request, 'game/item_detail.html',
                      context={'item': item, 'item_info': item_info})


class TaskDetail(generic.View):

    def get(self, request, *args, **kwargs):
        task_id = kwargs['task_id']
        task = Task.objects.prefetch_related('task').select_related('task__room__name').get(id=task_id)
        print(task)
        pass


class TaskList(generic.ListView):
    model = Task
    context_object_name = 'task_list'
    template_name = 'game/task_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Task.objects.filter(Q(creator=request.user) | Q(private=False))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)


class ItemList(generic.ListView):
    model = Item
    context_object_name = 'task_list'
    template_name = 'game/item_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Item.objects.filter(creator=request.user)
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)


