from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredientsViewSet,
                    TagsViewSet,
                    RecipesViewSet)

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipesViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
