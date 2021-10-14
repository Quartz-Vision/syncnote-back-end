from django.contrib import admin

# Register your models here.
from apps.notes.models import Tag, Note

admin.site.register(Note)
admin.site.register(Tag)