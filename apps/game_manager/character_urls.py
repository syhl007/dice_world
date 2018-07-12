from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import character_views

app_name = 'character'
urlpatterns = [
    path('list/', login_required(character_views.ListCharacter.as_view()), name='character_list'),
    path('list_from_group/<uuid:group_id>/', login_required(character_views.ListCharacter.as_view()), name='character_list_from_group'),
    path('list_from_room/<uuid:room_id>/', login_required(character_views.ListCharacter.as_view()), name='character_list_from_room'),
    path('link/', login_required(character_views.LinkCharacter.as_view()), name='character_link'),
    path('create/', login_required(character_views.CreateCharacter.as_view()), name='character_create'),
    path('<uuid:character_uuid>/', login_required(character_views.CharacterDetail.as_view()), name='character_detail'),
]
