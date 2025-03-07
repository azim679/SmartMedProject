import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from appointments.routing import websocket_urlpatterns  #Import WebSocket routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartMed.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  #Handles HTTP
    "websocket": AuthMiddlewareStack(  #Handles WebSockets
        URLRouter(websocket_urlpatterns)
    ),
})

#channel layer initialised
channel_layer = get_channel_layer()
