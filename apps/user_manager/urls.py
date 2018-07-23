from django.contrib.auth.decorators import login_required
from django.urls import path

from user_manager import views

app_name = 'user'
urlpatterns = [
    path('login/', views.Login.as_view(), name='user_login'),
    path('register/', views.Register.as_view(), name='user_register'),
    path('list/', login_required(views.ListUser.as_view()), name='user_list'),
]
