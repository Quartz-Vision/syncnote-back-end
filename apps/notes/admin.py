from django.contrib import admin

from apps.notes.models import Deletion, Note, Tag


admin.site.register(Tag)
admin.site.register(Note)
admin.site.register(Deletion)
