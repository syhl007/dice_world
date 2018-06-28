from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import views

app_name = 'character'
urlpatterns = [
    path('list/', login_required(views.ListCharacter.as_view()), name='character_list'),
    path('list/<uuid:group_id>/', login_required(views.ListCharacter.as_view()), name='character_list_from_group'),
    path('link/', login_required(views.LinkCharacter.as_view()), name='character_link'),
    path('create/', login_required(views.CreateCharacter.as_view()), name='character_create'),
    path('<uuid:character_uuid>/', login_required(views.CharacterDetail.as_view()), name='character_detail'),
]
