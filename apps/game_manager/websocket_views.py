from django.http import HttpResponse
from django.shortcuts import render
from dwebsocket import accept_websocket, require_websocket


@require_websocket
def private_chat(request):
    for message in request.websocket:
        request.websocket.send(message)  # 发送消息到客户端
