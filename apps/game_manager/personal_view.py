from django.db import transaction, connection
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views import generic

from game_manager.models import Character, Item


class ListCharacterSample(generic.ListView):
    model = Character
    template_name = 'personal/personal_character_simple.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Character.objects.filter(creator=request.user).order_by('-add_time')[0:5]
        return super().get(request, *args, **kwargs)


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'personal/personal_character_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Character.objects.filter(creator=request.user).order_by('-add_time')
        return super().get(request, *args, **kwargs)


class ListItemSample(generic.ListView):
    model = Item
    template_name = 'personal/personal_item_simple.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Item.objects.filter(creator=request.user).order_by('-add_time')[0:5]
        return super().get(request, *args, **kwargs)


class ListItem(generic.ListView):
    model = Item
    template_name = 'personal/personal_item_list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Item.objects.filter(creator=request.user).order_by('-add_time')
        return super().get(request, *args, **kwargs)
