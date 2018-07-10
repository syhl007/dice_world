from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import views

app_name = 'game'
urlpatterns = [
    path('create/task/', login_required(views.CreateTask.as_view()), name='task_create'),
    path('create/item/', login_required(views.CreateItem.as_view()), name='item_create'),
    path('item/<uuid:item_id>/', login_required(views.ItemDetail.as_view()), name='item_detail'),
    path('task/<uuid:task_id>/', login_required(views.TaskDetail.as_view()), name='task_detail'),
]
