from rest_framework import routers

from apps.notes.views import NotesViewSet

app_name = 'notes'

root_router = routers.SimpleRouter(trailing_slash=False)
root_router.register('', NotesViewSet, basename='notes')

urlpatterns = []

urlpatterns += root_router.urls
