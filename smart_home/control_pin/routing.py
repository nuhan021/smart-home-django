from django.urls import re_path
from .consumers import MyConsumer

websocket_urlpatterns = [
    re_path(r'ws/socket-server/', MyConsumer.as_asgi()),
]