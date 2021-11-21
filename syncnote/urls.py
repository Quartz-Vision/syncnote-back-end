from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

urlpatterns = [
    path('watch-tower/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/common/', include('apps.common.urls')),
    path('api/notes/', include('apps.notes.urls')),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="Syncnote",
            default_version='v1',
            description="Syncnote api for the data management",
        ),
        permission_classes=(permissions.AllowAny,),
        public=True,
    )

    urlpatterns += [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
    ]

urlpatterns = i18n_patterns(*urlpatterns)
