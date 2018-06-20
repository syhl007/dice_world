from django.urls import path

from user_manager import views

app_name = 'user'
urlpatterns = [
    path('login/', views.Login.as_view(), name='user_login'),
    path('list/', views.ListUser.as_view(), name='user_list'),
]
