from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import personal_view

app_name = 'personal'
urlpatterns = [
    path('self/list/character/sample/', login_required(personal_view.ListCharacterSample.as_view()),
         name='list_character_sample'),
    path('self/list/character/', login_required(personal_view.ListCharacter.as_view()),
         name='list_character'),
]
