from django.contrib.auth.models import User
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response

from recipes.models import (Ingredients,
                            Tags,
                            Recipes,
                            Favorite,
                            Subscribe,
                            Shopping,
                            IngredientsForRecipe)
from .filters import RecipeFilters
from .paginations import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientsSerializer,
                          TagsSerializer,
                          RecipesSerializer,
                          FavoriteSerializer,
                          SubscribeSerializer,
                          CustomUserSerializer,
                          CustomUserCreateSerializer)


class CustomUserViewSet(UserViewSet):
    """
    ViewsSet пользователя.
    """
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'subscribe' or self.action == 'subscriptions':
            return SubscribeSerializer
        if self.request.method == 'GET':
            return CustomUserSerializer
        return CustomUserCreateSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=[IsAuthenticated]
    )
    def subscribe(self, requests, id):
        if User.objects.get(id=id) == self.request.user:
            return Response(
                'Нельзя подписаться на себя',
                status=status.HTTP_400_BAD_REQUEST
            )
        if not User.objects.filter(id=id).exists():
            return Response(
                'Такого пользователя не существует',
                status=status.HTTP_404_NOT_FOUND
            )
        if self.request.method == 'POST':
            if Subscribe.objects.filter(
                    user_id=self.request.user.id,
                    author_id=id
            ).exists():
                return Response(
                    'Вы уже подписаны на этого человека',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(
                user_id=self.request.user.id,
                author_id=id
            )
            serializer = self.get_serializer(User.objects.get(id=id))
            return Response(serializer.data)
        if Subscribe.objects.filter(
                 user_id=self.request.user.id,
                author_id=id
        ).exists():
            Subscribe.objects.get(
                user_id=self.request.user.id,
                author_id=id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Вы не подписаны на этого человека',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        serializer_class=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(is_subscribe__user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet списка ингредиентов.
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'measurement_unit']


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet списка тегов.
    """
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = [AllowAny]


class RecipesViewSet(viewsets.ModelViewSet):
    """
    ViewSet рецептов.
    """
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilters

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
                return Response(
                    'Рецепт уже в избранном',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(
                user_id=self.request.user.id,
                recipe_id=pk
            )
            serializer = self.get_serializer(Recipes.objects.get(pk=pk))
            return Response(serializer.data)
        if Favorite.objects.filter(
                user_id=self.request.user,
                recipe_id=pk
        ).exists():
            Favorite.objects.get(
                user_id=self.request.user.id,
                recipe_id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта нету в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        if self.request.method == 'POST':
            if Shopping.objects.filter(
                user_id=self.request.user.id,
                recipe_id=pk
            ).exists():
                return Response(
                    'Рецепт уже в списке покупок',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Shopping.objects.create(
                user_id=self.request.user.id,
                recipe_id=pk
            )
            serializer = self.get_serializer(Recipes.objects.get(pk=pk))
            return Response(serializer.data)
        if Shopping.objects.filter(
                user_id=self.request.user.id,
                recipe_id=pk
        ).exists():
            Shopping.objects.get(
                user_id=self.request.user.id,
                recipe_id=pk
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'Рецепта нету в списке покупок',
            status=status.HTTP_400_BAD_REQUEST
        )

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
            file += f'{name}: {amount} {measurement_unit}\n'
        response = HttpResponse(file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response
