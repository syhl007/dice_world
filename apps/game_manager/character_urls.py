from django.contrib import admin
from django.urls import path

from game_manager import views

app_name = 'character'
urlpatterns = [
    path('list/', views.ListCharacter.as_view(), name='character_list'),
    # path('<uuid:character_uuid>/', None, name='detail'),
]
