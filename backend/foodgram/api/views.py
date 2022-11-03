from django.contrib.auth.models import User
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import (CustomUserSerializer,
                          CustomUserCreateSerializer,
                          IngredientsSerializer,
                          TagsSerializer,
                          RecipesSerializer)
from recipes.models import (Ingredients,
                            Tags,
                            Recipes)


class CustomUserViewSet(UserViewSet):
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        elif self.request.method == 'GET':
            return CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
