from django_socket_framework.types import BaseEventType


class NotesClientEventType(BaseEventType):
    MESSAGE = "message"
    AUTH = "auth"
