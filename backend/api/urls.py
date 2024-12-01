from django.urls import path, include
from rest_framework import routers

from .views import (
    UserViewSet, RecipeViewSet,
    IngredientViewSet, TagViewSet
)

router_v1 = routers.DefaultRouter()

router_v1.register('users', UserViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
