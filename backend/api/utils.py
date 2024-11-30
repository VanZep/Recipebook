from django.db.models import Sum
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError

from recipes.models import Recipe, IngredientRecipe


@require_GET
def short_url(request, pk):
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'/recipes/{pk}/')
    raise ValidationError({'detail': 'Рецепт не найден'})


def get_ingredients_in_shopping_cart(user):
    """Получение ингредиентов корзины покупок."""
    return (
        IngredientRecipe.objects.filter(
            recipe__recipes_in_cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount_sum=Sum('amount')
        )
    )
