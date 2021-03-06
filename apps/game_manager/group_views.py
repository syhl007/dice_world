from django.db.models import Q
from django.views import generic


from dice_world.standard import JsonResponse
from game_manager.models import GroupMember, Group, Room
from user_manager.models import User


class ListGroupCharacter(generic.ListView):
    queryset = GroupMember
    template_name = 'room/player_character_list.html'

    def get(self, request, *args, **kwargs):
        group = Group.objects.get(id=kwargs["group_id"])
        self.queryset = GroupMember.objects.select_related('user', 'character').filter(group=group).order_by(
            '-is_online')
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['group_id'] = group.id
        context['user_id'] = request.user.id
        context['is_gm'] = (group.room.gm == request.user)
        return self.render_to_response(context)


class KickOut(generic.View):

    def post(self, request, *args, **kwargs):
        group_id = kwargs['group_id']
        room = Room.objects.get(room__id=group_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg="权限不足")
        player = User.objects.get(id=kwargs['user_id'])
        GroupMember.objects.filter(Q(group__id=group_id) & Q(user=player)).delete()
        return JsonResponse(state=0)


class ShutUp(generic.View):

    def post(self, request, *args, **kwargs):
        group_id = kwargs['group_id']
        room = Room.objects.get(room__id=group_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg="权限不足")
        player = User.objects.get(id=kwargs['user_id'])
        GroupMember.objects.filter(Q(group__id=group_id) & Q(user=player)).update(send_msg=False)
        return JsonResponse(state=0)


class OpenMouth(generic.View):

    def post(self, request, *args, **kwargs):
        group_id = kwargs['group_id']
        room = Room.objects.get(room__id=group_id)
        if room.gm != request.user:
            return JsonResponse(state=2, msg="权限不足")
        player = User.objects.get(id=kwargs['user_id'])
        GroupMember.objects.filter(Q(group__id=group_id) & Q(user=player)).update(send_msg=True)
        return JsonResponse(state=0)


class InvitateToGame(generic.View):

    def post(self, request, *args, **kwargs):
        group_id = kwargs['group_id']
        room = Group.objects.get(id=group_id).room
        if room.gm != request.user:
            return JsonResponse(state=2, msg='权限不足')
        player = User.objects.get(id=request.POST['user_id'])
        GroupMember.objects.exclude(group__type=int(request.POST['type'])).filter(user=player).delete()
        try:
            group = Group.objects.get(Q(room=room) & Q(type=int(request.POST['type'])))
        except Group.DoesNotExist:
            return JsonResponse(state=2, msg="不具有对应组")
        try:
            GroupMember.objects.create(group=group, user=player)
            return JsonResponse(state=0)
        except Exception:
            return JsonResponse(state=2, msg='玩家已在游戏组中')

