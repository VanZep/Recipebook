from django.contrib import admin
from django.contrib.auth.models import Group

from core.constants import INLINE_EXTRA_FIELDS, MIN_NUM
from .models import (
    User, Recipe, Ingredient, Tag, Subscription,
    IngredientRecipe, FavoriteRecipe, ShoppingCart
)

admin.site.unregister(Group)
admin.site.empty_value_display = '-пусто-'


class RecipeIngredientsInLine(admin.TabularInline):
    model = IngredientRecipe
    extra = INLINE_EXTRA_FIELDS
    min_num = MIN_NUM


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
    readonly_fields = ('pub_date',)
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientsInLine,)

    def favorite_count(self, obj):
        return obj.recipes_in_favorite.count()

    favorite_count.short_description = 'У пользователей в избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('^name', 'name')
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'slug')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('user', 'author')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
