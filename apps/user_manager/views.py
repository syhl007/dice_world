import http

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic

from user_manager.models import User

from dice_world.standard import JsonResponse


class Login(generic.View):

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/html/main.html")
        else:
            return HttpResponse(status=http.HTTPStatus.UNAUTHORIZED)


class ListUser(generic.ListView):
    model = User
    template_name = 'user/user_list.html'
    ordering = '-last_login'

    def get(self, request, *args, **kwargs):
        return super(ListUser, self).get(request, *args, **kwargs)


class Register(generic.View):
    model = User
    template_name = 'user/user_create.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        try:
            User.objects.create_user(username=username, password=password)
        except Exception as e:
            return JsonResponse(state=2, msg='注册失败')
        return JsonResponse(state=0)
