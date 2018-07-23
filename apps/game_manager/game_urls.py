from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import game_views

app_name = 'game'
urlpatterns = [
    path('create/task/', login_required(game_views.CreateTask.as_view()), name='task_create'),
    path('create/item/', login_required(game_views.CreateItem.as_view()), name='item_create'),
    path('create/skill/', login_required(game_views.CreateSkill.as_view()), name='skill_create'),
    path('item/<uuid:item_id>/', login_required(game_views.ItemDetail.as_view()), name='item_detail'),
    path('task/<uuid:task_id>/', login_required(game_views.TaskDetail.as_view()), name='task_detail'),
    path('task_record/detail/', login_required(game_views.TaskRecordDetail.as_view()), name='task_record_detail'),
    path('skill/<uuid:skill_id>/', login_required(game_views.SkillDetail.as_view()), name='skill_detail'),
]
