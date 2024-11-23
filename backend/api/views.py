from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
)
from djoser import views

from recipes.models import Recipe, Ingredient, Tag, User, Subscription
from .serializers import (
    UserAvatarSerializer, RecipeSerializer, IngredientSerializer,
    TagSerializer, SubscriptionSerializer, SubscribeSerializer
)


class UserViewSet(views.UserViewSet):
    """Расширение передставления пользователя:
    добавление/удаление аватара;
    добавление/удаление подписки;
    список подписок.
    """

    # @action(
    #     methods=('put', 'delete'),
    #     detail=False,
    #     url_path='me/avatar'
    # )
    # def set_avatar(self, request, pk=None):
    #     """Настройка аватара пользователя."""
    #     user = request.user
    #     if request.method == 'PUT':
    #         serializer = UserAvatarSerializer(user, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=HTTP_200_OK)
    #     user.avatar.delete()
    #     return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('put',), detail=False, url_path='me/avatar')
    def avatar(self, request, pk=None):
        """Добавление аватара."""
        serializer = UserAvatarSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """Удаление аватара."""
        request.user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('post',), detail=True)
    def subscribe(self, request, id=None):
        """Добавление подписки."""
        author = get_object_or_404(User, pk=id)
        serializer = SubscribeSerializer(
            data={'author': author.id, 'user': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            SubscriptionSerializer(author).data, status=HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Удаление подписки."""
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(
            user=request.user.id, author=author.id
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            'Вы не подписаны на данного автора',
            status=HTTP_400_BAD_REQUEST
        )

    @action(methods=('get',), detail=False)
    def subscriptions(self, request, pk=None):
        """Список подписок."""
        print(request.data)
        queryset = User.objects.filter(is_subscribed=True)
        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class RecipeViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^title',)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
