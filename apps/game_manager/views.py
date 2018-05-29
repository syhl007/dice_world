from django.shortcuts import render
from django.views import generic

from game_manager.models import Character


class ListCharacter(generic.ListView):
    model = Character
    template_name = 'room/character_list.html'

