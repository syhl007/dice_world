import json
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic

from dice_world.standard import JsonResponse
from dice_world.utils import WordFilter
from game_manager.models import Character, Room, Group, GroupMember
from user_manager.models import User


class ListRoom(generic.ListView):
    model = Room
    template_name = 'room/room_list.html'
    ordering = '-add_time'

    def get(self, request, *args, **kwargs):
        return super(ListRoom, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        filter = request.POST['filter']
        print("[filter]", filter)
        if filter is not None:
            filter = json.loads(filter)
            print("[filter_loads]", filter)
        self.object_list = Room.objects.filter(**filter)
        context = self.get_context_data()
        response = self.render_to_response(context)
        return response


class CreateRoom(generic.CreateView):
    model = Room  # 生成的模型对象类、不设置这个的话就会去检测self.object和self.queryset来确定
    fields = ['name', ]  # 需要获取的字段，必须
    template_name = 'room/create_room.html'  # 当request以GET请求时返回的页面

    def form_valid(self, form):
        form.instance.gm = User.objects.all()[0]
        form.save()
        room = Room.objects.get(id=form.instance.id)
        game_players = Group()
        game_players.room = room
        game_players.type = 1
        game_players.save()
        GroupMember.objects.create(group=game_players, user=room.gm)
        if form.data.get('sidelines_allowed'):
            bystanders = Group()
            bystanders.room = room
            bystanders.save()
        return HttpResponse(JsonResponse(0, data={'room_id': str(room.id)}))

    # def form_invalid(self, form):
    #     print("[form_invalid]", form.instance)
    #     pass


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'room/character_list.html'


class ListGroupCharacter(generic.ListView):
    queryset = GroupMember
    template_name = 'room/character_list.html'



class RoomChat(generic.View):

    def post(self, request, *args, **kwargs):
        user = request.user
        room_id = kwargs.get('room_id')
        try:
            group = Group.objects.filter(room__id=room_id).get(user_set__contains=user)
        except (Group.DoesNotExist, Group.MultipleObjectsReturned):
            return None
        text = request.POST['text']
        text = WordFilter.handle(text)
        time = datetime.now()
        room = Room.objects.get(id=room_id)

        pass