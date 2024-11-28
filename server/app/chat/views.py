from django import http
from django.shortcuts import render


def index(request: http.HttpRequest) -> http.HttpResponse:
    return render(request, "chat/index.html")


def room(request: http.HttpRequest, room_name: str) -> http.HttpResponse:
    return render(request, "chat/room.html", {"room_name": room_name})
