"""dice_world URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include


def html_render(requeset, app_name=None, html=None):
    if app_name is None:
        return render(requeset, html)
    else:
        return render(requeset, app_name+"/"+html)


urlpatterns = [
    path('html/<str:html>', html_render),
    path('html/<str:app_name>/<str:html>', html_render),
    path('admin/', admin.site.urls),
    path('room/', include('game_manager.room_urls')),
    path('character/', include('game_manager.character_urls')),
    path('user/', include('user_manager.urls')),
]
