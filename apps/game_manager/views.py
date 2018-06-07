import json

from django.http import HttpResponse
from django.views import generic

from game_manager.models import Character, Room


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


class CreateRoom(generic.View):

    def post(self, request, *args, **kwargs):
        print(request.POST)
        print("post")
        return HttpResponse(json.dumps({'jas':'test'}), content_type='application/json')


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'room/character_list.html'
