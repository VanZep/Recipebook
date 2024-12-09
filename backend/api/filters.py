from rest_framework.filters import SearchFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import User, Recipe, Tag


class IngredientFilter(SearchFilter):
    """Фильтр ингредиентов."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='author',
        label='Автор'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        label='Избранные рецепты'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Рецепты в корзине'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipes_in_favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipes_in_cart__user=user)
        return queryset
