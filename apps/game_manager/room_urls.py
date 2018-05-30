from django.contrib import admin
from django.urls import path

from game_manager import views

app_name = 'rooms'
urlpatterns = [
    # path('list/', None, name='list'),
    # path('create/', None, name='create'),
    # path('drop/', None, name='drop'),
    # path('<uuid:room_uuid>/', None, name='detail'),
    path('<uuid:room_uuid>/list_character', views.ListCharacter.as_view(), name='list_character'),
]
