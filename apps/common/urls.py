from rest_framework import routers

from apps.common import views

app_name = 'common'


root_router = routers.SimpleRouter()
root_router.register('common', views.CommonViewSet, basename='common')

urlpatterns = root_router.urls
