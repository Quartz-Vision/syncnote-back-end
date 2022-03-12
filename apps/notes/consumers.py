from django_socket_framework.auth.consumers import AuthConsumer
from django_socket_framework.auth.middlewares import JWTAuthMiddleware

from apps.notes.method_lists import NotesMethodList
from apps.notes.event_lists import NotesEventList


class NotesConsumer(AuthConsumer):
    api_middlewares = (JWTAuthMiddleware.as_function(),)

    api_method_list_class = NotesMethodList
    event_method_list_class = NotesEventList
