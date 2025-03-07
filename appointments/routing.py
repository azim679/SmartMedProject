from django.urls import re_path
from appointments.consumers import VideoCallConsumer

#async route for websocket connection
websocket_urlpatterns = [
    re_path(r'ws/appointment/(?P<room_name>\w+)/$', VideoCallConsumer.as_asgi()),
]
