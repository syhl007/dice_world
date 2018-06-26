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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, include


def html_render(request, app_name=None, html=None):
    if not html.__contains__('login.html'):
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/html/login.html/")
    if app_name is None:
        return render(request, html)
    else:
        return render(request, app_name + "/" + html)


urlpatterns = [
    path('html/<str:html>/', html_render),
    path('html/<str:app_name>/<str:html>/', html_render),
    path('admin/', admin.site.urls),
    path('room/', include('game_manager.room_urls')),
    path('game/', include('game_manager.game_urls')),
    path('character/', include('game_manager.character_urls')),
    path('user/', include('user_manager.urls')),
]
