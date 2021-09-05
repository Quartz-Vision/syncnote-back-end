from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
)
from rest_framework import status, mixins, viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.user.serializers import UserCreateSerializer, UserRetrieveSerializer, CustomPasswordResetSerializer, \
    CustomPasswordResetConfirmSerializer

User = get_user_model()


class UserCreateView(generics.GenericAPIView):
    """
    User registration view
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        """
        Creates new user and returns it's auth token
        """
        serializer = self.get_serializer(
            instance=User.get_invited_or_none(request.data.get('email')),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        context = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }

        return Response(context, status=status.HTTP_201_CREATED)


class CurrentUserViewSet(generics.GenericAPIView):
    """
    User update view - for the currently logged in user
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserCreateSerializer

    @swagger_auto_schema(
        operation_description="Get the user that is logged in",
        responses={
            status.HTTP_200_OK: UserRetrieveSerializer()
        },
    )
    def get(self, request, *args, **kwargs):
        return Response(
            UserRetrieveSerializer(instance=request.user).data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_description="Get the user that is logged in",
        responses={
            status.HTTP_200_OK: UserRetrieveSerializer()
        },
        request_body=UserCreateSerializer()
    )
    def patch(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(
            instance=request.user,
            data=request.data
        )
        serializer.is_valid(True)
        serializer.save()
        return Response(
            UserRetrieveSerializer(instance=request.user).data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_description="Get the user that is logged in",
        responses={
            status.HTTP_200_OK: "OK"
        }
    )
    def delete(self, request, *args, **kwargs):
        request.user.delete()
        return Response(
            status=status.HTTP_200_OK
        )


class CustomPasswordResetView(PasswordResetView):
    serializer_class = CustomPasswordResetSerializer

    @swagger_auto_schema(
        operation_description="Sends password reset message to the email",
        responses={
            status.HTTP_200_OK: ""
        },
        request_body=CustomPasswordResetSerializer()
    )
    def post(self, *args, **kwargs):
        return super(CustomPasswordResetView, self).post(*args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = CustomPasswordResetConfirmSerializer

    @swagger_auto_schema(
        operation_description="Reset the password using codes from the email",
        responses={
            status.HTTP_200_OK: ""
        },
        request_body=CustomPasswordResetConfirmSerializer()
    )
    def post(self, *args, **kwargs):
        return super(CustomPasswordResetConfirmView, self).post(*args, **kwargs)

    @swagger_auto_schema(
        operation_description="Reset the password using codes from the email",
        responses={
            status.HTTP_200_OK: ""
        }
    )
    def get(self, *args, **kwargs):
        return Response({
            "uid": self.request.query_params.get("uid"),
            "token": self.request.query_params.get("token")
        }, template_name='password_reset_confirm.html')


class CustomPasswordResetSuccessView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)

    @swagger_auto_schema(
        operation_description="Password reset success page",
        responses={
            status.HTTP_200_OK: ""
        }
    )
    def get(self, *args, **kwargs):
        return Response({}, template_name='password_reset_success.html')
