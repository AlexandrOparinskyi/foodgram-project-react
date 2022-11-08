from django.contrib.auth.models import User
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse

from .serializers import (CustomUserSerializer,
                          CustomUserCreateSerializer,
                          IngredientsSerializer,
                          TagsSerializer,
                          RecipesSerializer,
                          FavoriteSerializer)
from recipes.models import (Ingredients,
                            Tags,
                            Recipes,
                            Favorite,
                            Subscribe,
                            Shopping,
                            IngredientsForRecipe)
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

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, requests, pk):
        if self.request.method == 'POST':
            Subscribe.objects.create(
                user_id=self.request.user.id,
                author_id=pk
            )
            return Response(status=status.HTTP_201_CREATED)
        Subscribe.objects.get(
            user_id=self.request.user.id,
            author_id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    ViewSet списка ингредиентов.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = None


class TagsViewSet(viewsets.ModelViewSet):
    """
    ViewSet списка тегов.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return FavoriteSerializer
        return RecipesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        if self.request.method == 'POST':
            if Favorite.objects.filter(
                user_id=self.request.user,
                recipe_id=pk
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(
                user_id=self.request.user.id,
                recipe_id=pk
            )
            serializer = self.get_serializer(Recipes.objects.get(pk=pk))
            return Response(serializer.data)
        Favorite.objects.get(
            user_id=self.request.user.id,
            recipe_id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        if self.request.method == 'POST':
            if Shopping.objects.filter(
                user_id=self.request.user.id,
                recipe_id=pk
            ).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Shopping.objects.create(
                user_id=self.request.user.id,
                recipe_id=pk
            )
            serializer = self.get_serializer(Recipes.objects.get(pk=pk))
            return Response(serializer.data)
        Shopping.objects.get(
            user_id=self.request.user.id,
            recipe_id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = IngredientsForRecipe.objects.filter(
            recipe__shopping_recipe__user=self.request.user
        ).values_list(
            'ingredients__name', 'ingredients__measurement_unit', 'amount'
        ).order_by(
            'ingredients__name'
        )
        file = 'Список покупок:\n'
        for ingredients in shopping_cart:
            name, measurement_unit, amount = ingredients
            file += f'{name}: {amount} {measurement_unit}'
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response
