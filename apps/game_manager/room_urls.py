from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import views

app_name = 'room'
urlpatterns = [
    path('list/', login_required(views.ListRoom.as_view()), name='room_list'),
    path('create/', login_required(views.CreateRoom.as_view()), name='room_create'),
    # path('drop/', None, name='drop'),
    path('<uuid:pk>/', login_required(views.RoomDetail.as_view()), name='room_detail'),
    path('<uuid:room_id>/join/', login_required(views.JoinRoom.as_view()), name='room_join'),
    path('<uuid:room_id>/chat/', login_required(views.RoomChat.as_view()), name='room_chat'),
    path('<uuid:room_id>/chat/save/', login_required(views.SaveRoomChat.as_view()), name='room_chat'),
    path('<uuid:room_id>/list/group/', login_required(views.ListGroup.as_view()), name='list_group'),
    path('<uuid:room_id>/list/character/<uuid:group_id>/', login_required(views.ListGroupCharacter.as_view()),
         name='list_character'),
    path('<uuid:room_id>/kick_out/<uuid:user_id>/', login_required(views.KickOut.as_view()),
         name='kick_out'),
    path('<uuid:room_id>/shut_up/<uuid:user_id>/', login_required(views.ShutUp.as_view()),
         name='shut_up'),
]
