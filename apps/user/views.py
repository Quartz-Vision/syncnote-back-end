from django.contrib.auth import get_user_model
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from dj_rest_auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
)
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.serializers import (
    UserCreateSerializer,
    UserRetrieveSerializer,
    CustomPasswordResetSerializer,
    CustomPasswordResetConfirmSerializer,
    UserUpdateSerializer
)

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
        serializer = self.get_serializer(data=request.data)
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
    serializer_class = UserUpdateSerializer

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
        serializer = UserUpdateSerializer(
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
        }, template_name='user/password_reset_confirm.html')


class CustomPasswordResetSuccessView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)

    @swagger_auto_schema(
        operation_description="Password reset success page",
        responses={
            status.HTTP_200_OK: ""
        }
    )
    def get(self, *args, **kwargs):
        print(reverse('user:password_reset_success'))
        return Response({}, template_name='user/password_reset_success.html')
