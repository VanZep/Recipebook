from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import views

from recipes.models import Recipe, Ingredient, Tag
from .serializers import (
    UserAvatarSerializer, RecipeSerializer, IngredientSerializer, TagSerializer
)


class UserViewSet(views.UserViewSet):
    """Расширение передставления пользователя для:
    настройки аватара пользователя,
    """

    @action(
        methods=('put', 'delete'),
        detail=False,
        url_path='me/avatar',
        serializer_class=UserAvatarSerializer
    )
    def set_avatar(self, request, pk=None):
        """Настройка аватара пользователя."""
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
