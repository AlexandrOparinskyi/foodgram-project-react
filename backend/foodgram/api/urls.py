from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredientsViewSet,
                    TagsViewSet,
                    RecipesViewSet,
                    CustomUserViewSet)

router = DefaultRouter()

router.register('users', CustomUserViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
