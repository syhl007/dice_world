from django.urls import path

from user_manager import views

app_name = 'user'
urlpatterns = [
    path('list/', views.ListUser.as_view(), name='user_list'),
]
