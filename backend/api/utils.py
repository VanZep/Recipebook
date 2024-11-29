from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError

from recipes.models import Recipe


@require_GET
def short_url(request, pk):
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'/recipes/{pk}/')
    raise ValidationError({'detail': 'Рецепт не найден'})
