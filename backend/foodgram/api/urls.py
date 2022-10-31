from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredientsViewSet,
                    TagsViewSet)

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
