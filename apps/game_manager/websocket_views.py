import json

from django.contrib import auth
from django.db.models import Q
from dwebsocket import require_websocket

from dice_world.standard import global_websocket_dict
from game_manager.models import Group, GroupMember


@require_websocket
def private_chat(request, *args, **kwargs):
    global_websocket_dict[request.user] = request.websocket
    for message in request.websocket:
        try:
            if not message:
                global_websocket_dict.pop(request.user)
                try:
                    group = GroupMember.objects.get(user=request.user, is_online=True).group
                    users = group.users.all()
                    for user in users:
                        w = global_websocket_dict.get(user)
                        if w and request.user != user:
                            w.send(json.dumps({'system_order': 'refresh_character', 'group_id': str(group.id)}).encode(
                                encoding='utf-8'))
                except Exception as e:
                    pass
                GroupMember.objects.filter(user=request.user).update(is_online=False)
                break
            # print("message::", message)
            data = json.loads(str(message, encoding='utf-8'))
            if data.get('system_order'):
                if data.get('system_order') == 'refresh_character':
                    group_id = data.get('group_id')
                    members = GroupMember.objects.filter(group__id=group_id, is_online=True).all()
                    for member in members:
                        w = global_websocket_dict.get(member.user)
                        if w and request.user != member.user:
                            w.send(json.dumps({'system_order': 'refresh_character','group_id':group_id}).encode(encoding='utf-8'))
            else:
                sender = request.user
                receiver = auth.get_user_model().objects.get(id=data.get('receiver'))
                type = data.get('type')
                group_id = data.get('group_id')
                msg = data.get('msg')
                if msg:
                    ws = global_websocket_dict.get(receiver)
                    if ws:
                        group = Group.objects.select_related('room').get(id=group_id)
                        room = group.room
                        member = GroupMember.objects.select_related('character').get(Q(user=sender) & Q(group=group))
                        if member.character:
                            name = member.character.name
                        else:
                            name = '神秘声音'
                        chat_message = {'sender': name, 'room': room.name, 'group': group.type, 'msg': msg}
                        ws.send(json.dumps(chat_message).encode(encoding='utf-8'))
        except Exception as e:
            print("[websocket error]", e)
            continue
