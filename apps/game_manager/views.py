from django.shortcuts import render
from django.views import generic

from game_manager.models import Character, Room


class ListRoom(generic.ListView):
    model = Room
    template_name = 'room/room_list.html'

    def get_queryset(self):
        print("[test]", self.kwargs)
        return Room.objects.order_by('-add_time')

    def post(self, request, *args, **kwargs):
        print("test")
        return self.get(request, *args, **kwargs)


class RoomDetail(generic.DetailView):
    model = Room
    template_name = 'room/room_detail.html'


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'room/character_list.html'
