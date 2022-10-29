from djoser.views import UserViewSet
from .serializers import CustomUserSerializer, CustomUserCreateSerializer
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination


class CustomUserViewSet(UserViewSet):
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        elif self.request.method == 'GET':
            return CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()
