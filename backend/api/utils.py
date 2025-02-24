from django.db.models import Sum
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from recipes.models import Recipe, IngredientRecipe
from .validators import is_not_exists_objects_validator


@require_GET
def get_short_url(request, pk):
    """Получение короткой ссылки на рецепт."""
    recipes = Recipe.objects.filter(pk=pk)
    is_not_exists_objects_validator(recipes, 'Рецепт не найден')
    return redirect(f'/recipes/{pk}/')


def get_ingredients_in_shopping_cart(user):
    """Получение ингредиентов корзины покупок."""
    return (
        IngredientRecipe.objects.filter(
            recipe__recipes_in_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
    )


def get_list_of_ingredients_string(ingredients):
    """Формирование списка ингредиентов."""
    return '\n'.join(
        f'{i+1}.{ingredient.get("ingredient__name").capitalize()} - '
        f'{ingredient.get("total_amount")} '
        f'({ingredient.get("ingredient__measurement_unit")})'
        for i, ingredient in enumerate(ingredients)
    )


def get_subscription_objects(user, author):
    """Получение подписок."""
    return author.subscribing.filter(user=user)


def get_favorite_recipe_objects(user, recipe):
    """Получение избранных рецептов."""
    return user.favorite_recipes.filter(recipe=recipe)


def get_shopping_cart_objects(user, recipe):
    """Получение рецептов, находящихся в корзине покупок."""
    return user.recipes_in_cart.filter(recipe=recipe)
