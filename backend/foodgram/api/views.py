from django.contrib.auth.models import User
from djoser.views import UserViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import CustomUserSerializer, CustomUserCreateSerializer


class CustomUserViewSet(UserViewSet):
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        elif self.request.method == 'GET':
            return CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()
