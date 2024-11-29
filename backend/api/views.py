from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
)
from djoser import views

from recipes.models import (
    Recipe, Ingredient, Tag, User, Subscription, FavoriteRecipe
)
from .serializers import (
    UserAvatarSerializer, RecipeWriteSerializer, RecipeReadSerializer,
    IngredientSerializer, TagSerializer, SubscriptionSerializer,
    AddRecipeSerializer
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
    def avatar(self, request):
        """Добавление аватара."""
        serializer = UserAvatarSerializer(
            request.user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        request.user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('post',), detail=True)
    def subscribe(self, request, id=None):
        """Добавление подписки."""
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            user=request.user.id, author=author.id
        ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на данного автора'}
            )
        if request.user.id == author.id:
            return Response(
                {'detail': 'Нельзя подписаться на себя'}
            )
        subscription = Subscription.objects.create(
            user=request.user, author=author
        )
        # subscription.save()
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data, status=HTTP_201_CREATED)
        # sub = Subscription(user=request.user, author=author)
        # serializer = SubscribeSerializer(sub)
        # sub.save()
        # serializer = SubscribeSerializer(
        #     data={'author': author.id, 'user': request.user.id}
        # )
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # author.is_subscribed = True
        # author.save()
        # return Response(
        #     SubscriptionSerializer(author).data, status=HTTP_201_CREATED
        # )
        # return Response(
        #     serializer.data, status=HTTP_201_CREATED
        # )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Удаление подписки."""
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=request.user.id, author=author.id
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Вы не подписаны на данного автора'},
            status=HTTP_400_BAD_REQUEST
        )
        # if self.is_exists:
        #     subscription.delete()
        #     return Response(status=HTTP_204_NO_CONTENT)
        # return Response(
        #     {'detail': 'Вы не подписаны на данного автора'},
        #     status=HTTP_400_BAD_REQUEST
        # )

    def is_exists(self, user, model, obj):
        return model.objects.filter(user=user, author=obj).exists()

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        """Список подписок."""
        queryset = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data, status=HTTP_200_OK)


class RecipeViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post',), detail=True)
    def favorite(self, request, pk=None):
        """Добавление в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {'detail': 'Данный рецепт уже находится у вас в избранном'}
            )
        if request.user == recipe.author:
            return Response(
                {'detail': 'Нельзя добавить в избранное свой рецепт'}
            )
        favorite_recipe = FavoriteRecipe.objects.create(
            user=request.user, recipe=recipe
        )
        serializer = AddRecipeSerializer(
            favorite_recipe, context={'request': request}
        )
        return Response(serializer.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        """Удаление из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_recipe = FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        )
        if favorite_recipe.exists():
            favorite_recipe.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'У вас в избранном нет такого рецепта'},
            status=HTTP_400_BAD_REQUEST
        )
        # if self.is_exists(request.user, FavoriteRecipe, recipe):
        #     favorite_recipe.delete()
        #     return Response(status=HTTP_204_NO_CONTENT)
        # return Response(
        #     {'detail': 'У вас в избранном нет такого рецепта'},
        #     status=HTTP_400_BAD_REQUEST
        # )

    def is_exists(self, user, model, obj):
        return model.objects.filter(user=user, recipe=obj).exists()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
