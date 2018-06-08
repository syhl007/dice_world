import json

from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic

from dice_world.standard import JsonResponse
from game_manager.models import Character, Room
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
        id = Room.objects.get(id=form.instance.id).id
        return HttpResponse(JsonResponse(0, data={'room_id': str(id)}))

    # def form_invalid(self, form):
    #     print("[form_invalid]", form.instance)
    #     pass


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'room/character_list.html'
