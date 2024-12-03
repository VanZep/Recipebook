from django.contrib import admin

from core.constants import INLINE_EXTRA_FIELDS
from .models import (
    User, Recipe, Ingredient, Tag, Subscription,
    IngredientRecipe, FavoriteRecipe, ShoppingCart
)

admin.site.empty_value_display = '-пусто-'


class RecipeIngredientsInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = INLINE_EXTRA_FIELDS


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ('username', 'email')
    fields = (
        'username', 'email',
        ('first_name', 'last_name'),
        'password', 'avatar'
    )
    search_fields = ('username', 'email')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username')
    readonly_fields = ('pub_date', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientsInLine,)

    def favorite_count(self, obj):
        return obj.recipes_in_favorite.count()

    favorite_count.short_description = 'У пользователей в избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    search_fields = ('^name', 'name')


admin.site.register(Tag)
admin.site.register(Subscription)
admin.site.register(FavoriteRecipe)
admin.site.register(ShoppingCart)
