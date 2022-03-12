from django.urls import re_path

from apps.notes import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.NotesConsumer.as_asgi()),
]
