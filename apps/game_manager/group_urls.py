from django.contrib.auth.decorators import login_required
from django.urls import path

from game_manager import group_views

app_name = 'group'
urlpatterns = [
    path('<uuid:group_id>/list/character/', login_required(group_views.ListGroupCharacter.as_view()),
         name='list_character'),
    path('<uuid:group_id>/kick_out/<uuid:user_id>/', login_required(group_views.KickOut.as_view()),
         name='kick_out'),
    path('<uuid:group_id>/shut_up/<uuid:user_id>/', login_required(group_views.ShutUp.as_view()),
         name='shut_up'),
]
