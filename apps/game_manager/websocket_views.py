import json

from django.contrib import auth
from django.db.models import Q
from dwebsocket import require_websocket

from dice_world.standard import global_websocket_dict
from game_manager.models import Group, GroupMember, UserLinkRoom


@require_websocket
def private_chat(request, *args, **kwargs):
    global_websocket_dict[request.user] = request.websocket
    for message in request.websocket:
        try:
            if not message:
                global_websocket_dict.pop(request.user)
                UserLinkRoom.objects.filter(user=request.user).delete()
                break
            print("message::", message)
            data = json.loads(str(message, encoding='utf-8'))
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
                    chat_message = {'sender': name, 'room': room, 'group': group, 'msg': msg}
                    ws.send(json.dumps(chat_message).encode(encoding='utf-8'))
                pass
        except Exception as e:
            print("[socket]", e)
            continue
