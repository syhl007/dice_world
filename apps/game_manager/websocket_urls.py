from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import websocket_views

app_name = 'websocket'
urlpatterns = [
    path('private_chat/', websocket_views.private_chat, name='private_chat'),
    path('private_chat/<uuid:send_to_id>/', websocket_views.private_chat, name='private_chat_1'),
]
