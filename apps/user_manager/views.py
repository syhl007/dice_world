from django.shortcuts import render
from django.views import generic

from user_manager.models import User


class ListUser(generic.ListView):
    model = User
    template_name = 'user/user_list.html'
    ordering = '-last_login'

    def get(self, request, *args, **kwargs):
        return super(ListUser, self).get(request, *args, **kwargs)
