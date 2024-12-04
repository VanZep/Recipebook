from django.db.models import Sum
from django.shortcuts import redirect

from recipes.models import Recipe, IngredientRecipe
from .validators import is_not_exists_objects_validator


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
