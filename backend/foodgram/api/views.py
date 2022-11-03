from django.contrib.auth.models import User
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .serializers import (CustomUserSerializer,
                          CustomUserCreateSerializer,
                          IngredientsSerializer,
                          TagsSerializer,
                          RecipesSerializer)
from recipes.models import (Ingredients,
                            Tags,
                            Recipes)
from .permissions import IsAuthorOrReadOnly


class CustomUserViewSet(UserViewSet):
    """
    ViewsSet пользователя.
    """
    http_method_names = ['post', 'get']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        elif self.request.method == 'GET':
            return CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    ViewSet списка ингредиентов.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    """
    ViewSet списка тегов.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = [IsAuthorOrReadOnly]
    permission_classes = [AllowAny]
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
