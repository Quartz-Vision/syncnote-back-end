from django_socket_framework.method_lists import BaseConsumerMethodList
from django_socket_framework.types import ClientEvent

from apps.notes.type import NotesClientEventType


class NotesMethodList(BaseConsumerMethodList):
    async def auth(self, __response_client_data=None):
        return ClientEvent(NotesClientEventType.AUTH, __response_client_data)

    async def add_group(self, group_id):
        await self.consumer.attach_group(str(group_id))

    async def send_message(self, group_id, text=''):
        await self.consumer.send_group_event(str(group_id), 'new_message', kwargs={
            'text': text
        })
