from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenObtainPairView
)

from apps.user.views import (
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetSuccessView,
    CurrentUserViewSet,
    UserCreateView
)

app_name = 'user'

root_router = routers.SimpleRouter()

urlpatterns = [
    path('auth/', TokenObtainPairView.as_view()),
    path('refresh-token/', TokenRefreshView.as_view()),
    path('verify-token/', TokenVerifyView.as_view()),
    path('register/', UserCreateView.as_view()),

    path('reset-password/', CustomPasswordResetView.as_view()),
    path('reset-password/confirm/',
         CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset-password/success/',
         CustomPasswordResetSuccessView.as_view(),
         name='password_reset_success'),
    path('profile/', CurrentUserViewSet.as_view())
]
