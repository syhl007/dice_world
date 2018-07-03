import json

from django.contrib import auth
from dwebsocket import require_websocket

from dice_world.standard import global_websocket_dict


@require_websocket
def private_chat(request, *args, **kwargs):
    global_websocket_dict[request.user] = request.websocket
    for message in request.websocket:
        try:
            print("message::", message)
            data = json.loads(str(message, encoding='utf-8'))
            sender = request.user
            receiver = auth.get_user_model().objects.get(id=data.get('receiver'))
            type = data.get('type')
            room_id = data.get('room_id')
            msg = data.get('msg')
            if msg:
                ws = global_websocket_dict.get(receiver)
                if ws:
                    ws.send(msg.encode(encoding='utf-8'))
                pass
        except Exception as e:
            continue
        # request.websocket.send(message)  # 发送消息到客户端
