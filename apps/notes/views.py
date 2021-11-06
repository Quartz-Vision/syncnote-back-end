# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from apps.notes.serializers import NoteSerializer


class NotesViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    User update view - for the currently logged in user
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = NoteSerializer

    def get_queryset(self):
        return self.request.user.notes.all()
