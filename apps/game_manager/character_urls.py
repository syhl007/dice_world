from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import character_views

app_name = 'character'
urlpatterns = [
    path('list/', login_required(character_views.ListCharacter.as_view()), name='character_list'),
    path('list_from_group/<uuid:group_id>/', login_required(character_views.ListCharacter.as_view()), name='character_list_from_group'),
    path('list_from_room/<uuid:room_id>/', login_required(character_views.ListCharacter.as_view()), name='character_list_from_room'),
    path('list_npc/<uuid:task_id>/', login_required(character_views.ListNPC.as_view()), name='list_npc'),
    path('add_npc/', login_required(character_views.AddNPC.as_view()), name='add_npc'),
    path('link/', login_required(character_views.LinkCharacter.as_view()), name='character_link'),
    path('create/', login_required(character_views.CreateCharacter.as_view()), name='character_create'),
    path('<uuid:character_uuid>/', login_required(character_views.CharacterDetail.as_view()), name='character_detail'),
]
