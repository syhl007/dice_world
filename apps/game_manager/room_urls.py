from django.contrib import admin
from django.urls import path

from game_manager import views

app_name = 'room'
urlpatterns = [
    path('list/', views.ListRoom.as_view(), name='room_list'),
    path('create/', views.CreateRoom.as_view(), name='room_create'),
    # path('create/', None, name='create'),
    # path('drop/', None, name='drop'),
    path('<uuid:pk>/', views.RoomDetail.as_view(), name='room_detail'),
    path('<uuid:room_id>/chat/', views.RoomChat.as_view(), name='room_chat'),
    path('<uuid:pk>/list_character/', views.ListCharacter.as_view(), name='list_character'),
]
