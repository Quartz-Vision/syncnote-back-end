from django_socket_framework.method_lists import BaseConsumerMethodList
from django_socket_framework.types import ClientEvent

from apps.notes.type import NotesClientEventType


class NotesEventList(BaseConsumerMethodList):
    async def new_message(self, text, *args, __response_client_data=None, **kwargs):
        await self.consumer.send_json(ClientEvent(
            NotesClientEventType.MESSAGE,
            __response_client_data,
            text=text
        ))
