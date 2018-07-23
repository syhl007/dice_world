from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import room_views

app_name = 'room'
urlpatterns = [
    path('list/', login_required(room_views.ListRoom.as_view()), name='room_list'),
    path('create/', login_required(room_views.CreateRoom.as_view()), name='room_create'),
    path('<uuid:pk>/', login_required(room_views.RoomDetail.as_view()), name='room_detail'),
    path('<uuid:room_id>/join/', login_required(room_views.JoinRoom.as_view()), name='room_join'),
    path('<uuid:room_id>/chat/', login_required(room_views.RoomChat.as_view()), name='room_chat'),
    path('<uuid:room_id>/start/', login_required(room_views.StartGame.as_view()), name='game_start'),
    path('<uuid:room_id>/end/', login_required(room_views.EndGame.as_view()), name='game_end'),
    path('<uuid:room_id>/chat/save/', login_required(room_views.SaveRoomChat.as_view()), name='game_save'),
    path('<uuid:room_id>/list/group/', login_required(room_views.ListGroup.as_view()), name='list_group'),
    path('<uuid:room_id>/list/player/', login_required(room_views.ListPlayer.as_view()), name='list_player'),
    path('<uuid:room_id>/list/task/', login_required(room_views.ListTask.as_view()), name='list_task'),
    path('<uuid:room_id>/add/task/', login_required(room_views.TaskAdd.as_view()), name='add_task'),
    path('<uuid:room_id>/start/task/', login_required(room_views.StartTask.as_view()), name='start_task'),
    path('<uuid:room_id>/record/task/', login_required(room_views.RecordTask.as_view()), name='record_task'),
    path('<uuid:room_id>/list/item/', login_required(room_views.ListItem.as_view()), name='list_item'),
    path('<uuid:room_id>/get/item/', login_required(room_views.ItemGet.as_view()), name='get_item'),
    path('<uuid:room_id>/lost/item/', login_required(room_views.ItemLost.as_view()), name='lost_item'),
    path('<uuid:room_id>/change/item/', login_required(room_views.ItemChange.as_view()), name='change_item'),
    path('<uuid:room_id>/add/item/', login_required(room_views.ItemAdd.as_view()), name='add_item'),
    path('<uuid:room_id>/list/skill/', login_required(room_views.ListSkill.as_view()), name='list_skill'),
    path('<uuid:room_id>/get/skill/', login_required(room_views.SkillGet.as_view()), name='get_skill'),
    path('<uuid:room_id>/lost/skill/', login_required(room_views.SkillLost.as_view()), name='lost_skill'),
    path('<uuid:room_id>/add/skill/', login_required(room_views.SkillAdd.as_view()), name='add_skill'),
    path('<uuid:room_id>/record/task/<uuid:task_record_id>', login_required(room_views.TaskRecordDetail.as_view()), name='record_task_detail'),


]
