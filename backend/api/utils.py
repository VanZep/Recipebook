from django.db.models import Sum
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError

from recipes.models import Recipe, IngredientRecipe
from .validators import is_not_exists_objects_validator


def is_subscribed(user, author):
    """"""
    return user.subscribers.filter(author=author).exists()


# def is_exists_objects(model, user, obj):
#     """Функция проверки, что объекты существуют."""
#     return model.objects.filter(
#         user=user, recipe=obj
#     ).exists()


# @require_GET
def get_short_url(request, pk):
    """Получение короткой ссылки на рецепт."""
    recipes = Recipe.objects.filter(pk=pk)
    is_not_exists_objects_validator(recipes, 'Рецепт не найден')
    # if Recipe.objects.filter(pk=pk).exists():
    return redirect(f'/recipes/{pk}/')
    # raise ValidationError({'detail': 'Рецепт не найден'})


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
