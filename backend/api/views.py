from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import User, Recipe, Ingredient, Tag
from .serializers import (
    UserAvatarSerializer, RecipeWriteSerializer, RecipeReadSerializer,
    IngredientSerializer, TagSerializer, SubscriptionSerializer,
    RecipeShortSerializer, CreateSubscriptionSerializer,
    CreteFavoriteRecipeSerializer, CreateShoppingCartSerializer
)
from .utils import (
    get_ingredients_in_shopping_cart, get_list_of_ingredients_string,
    get_subscription_objects, get_favorite_recipe_objects,
    get_shopping_cart_objects
)
from .pagination import PageNumberLimitPagination
from .validators import is_not_exists_objects_validator
from .permissions import IsAuthenticatedOrIsAuthorOrReadOnly


class UserViewSet(DjoserUserViewSet):
    """Расширение передставления пользователя:
    добавление/удаление аватара;
    добавление/удаление подписки;
    список подписок.
    """

    pagination_class = PageNumberLimitPagination

    @action(methods=('put',), detail=False, url_path='me/avatar')
    def avatar(self, request):
        """Добавление аватара."""
        serializer = UserAvatarSerializer(
            request.user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        request.user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('post',), detail=True)
    def subscribe(self, request, id=None):
        """Добавление подписки."""
        author = get_object_or_404(User, id=id)
        serializer = CreateSubscriptionSerializer(
            data={"user": request.user.id, "author": author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            SubscriptionSerializer(author, context={'request': request}).data,
            status=HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Удаление подписки."""
        author = get_object_or_404(User, id=id)
        subscriptions = get_subscription_objects(request.user, author)
        is_not_exists_objects_validator(
            subscriptions, 'Вы не подписаны на данного автора'
        )
        subscriptions.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок."""
        queryset = [obj.author for obj in request.user.subscribers.all()]
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrIsAuthorOrReadOnly,)
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('get',), detail=True, url_path='get-link',
        permission_classes=(IsAuthenticated,),
    )
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = get_object_or_404(Recipe, pk=pk)
        link = reverse('short_url', args=[recipe.pk])
        return Response(
            {'short-link': request.build_absolute_uri(link)}
        )

    @action(methods=('post',), detail=True)
    def favorite(self, request, pk=None):
        """Добавление в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = CreteFavoriteRecipeSerializer(
            data={"user": request.user.id, "recipe": recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeShortSerializer(recipe, context={'request': request}).data,
            status=HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        """Удаление из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite_recipes = get_favorite_recipe_objects(
            request.user, recipe
        )
        is_not_exists_objects_validator(
            favorite_recipes, 'У вас в избранном нет такого рецепта'
        )
        favorite_recipes.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=('post',), detail=True)
    def shopping_cart(self, request, pk=None):
        """Добавление в корзину."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = CreateShoppingCartSerializer(
            data={"user": request.user.id, "recipe": recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeShortSerializer(recipe, context={'request': request}).data,
            status=HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        """Удаление из корзины."""
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_cart_recipes = get_shopping_cart_objects(
            request.user, recipe
        )
        is_not_exists_objects_validator(
            shopping_cart_recipes,
            'У вас в корзине нет такого рецепта'
        )
        shopping_cart_recipes.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get',), detail=False, permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Загрузка списка ингредиентов из корзины."""
        ingredients = get_ingredients_in_shopping_cart(request.user)
        is_not_exists_objects_validator(ingredients, 'В корзине ничего нет')
        return FileResponse(
            get_list_of_ingredients_string(ingredients),
            filename='shopping_cart.txt'
        )


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('^name', 'name')
    permission_classes = (IsAdminUser,)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)
