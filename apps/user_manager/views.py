from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic

from user_manager.models import User


class Login(generic.View):

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/html/main.html")
        else:
            return HttpResponse()


class ListUser(generic.ListView):
    model = User
    template_name = 'user/user_list.html'
    ordering = '-last_login'

    def get(self, request, *args, **kwargs):
        return super(ListUser, self).get(request, *args, **kwargs)
