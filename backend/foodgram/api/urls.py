from django.urls import include, path
from rest_framework.authtoken import views

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
