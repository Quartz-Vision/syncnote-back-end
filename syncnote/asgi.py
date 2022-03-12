import os

from syncnote.wsgi import *
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.notes import routing as notes_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casamsa.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notes_routing.websocket_urlpatterns
        )
    ),
})
