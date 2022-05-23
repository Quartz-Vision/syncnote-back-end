from datetime import datetime
from typing import TypedDict

from django_socket_framework.types import BaseEventType


class NotesClientEventType(BaseEventType):
    MESSAGE = "message"
    AUTH = "auth"


class ActionDict(TypedDict):
    note_id: str
    time: datetime


class ClientServerIdsDict(TypedDict):
    server_note_id: str
    client_note_id: str
