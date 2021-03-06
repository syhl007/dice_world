from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import personal_view

app_name = 'personal'
urlpatterns = [
    path('self/list/character/sample/', login_required(personal_view.ListCharacterSample.as_view()),
         name='list_character_sample'),
    path('self/list/character/', login_required(personal_view.ListCharacter.as_view()),
         name='list_character'),
    path('del/character/', login_required(personal_view.DelCharacter.as_view()), name='delete_character'),
    path('self/list/item/sample/', login_required(personal_view.ListItemSample.as_view()),
         name='list_item_sample'),
    path('self/list/item/', login_required(personal_view.ListItem.as_view()),
         name='list_item'),
    path('self/list/task/sample/', login_required(personal_view.ListTaskSample.as_view()),
         name='list_task_sample'),
    path('del/item/', login_required(personal_view.DelItem.as_view()), name='delete_item'),
    path('self/list/task/', login_required(personal_view.ListTask.as_view()),
         name='list_task'),
    path('self/list/skill/sample/', login_required(personal_view.ListSkillSample.as_view()),
         name='list_skill_sample'),
    path('self/list/skill/', login_required(personal_view.ListSkill.as_view()),
         name='list_skill'),
    path('del/skill/', login_required(personal_view.DelSkill.as_view()), name='delete_skill'),
]
