from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from core.constants import INLINE_EXTRA_FIELDS, MIN_NUM
from .models import (
    User, Recipe, Ingredient, Tag, Subscription,
    IngredientRecipe, FavoriteRecipe, ShoppingCart
)

admin.site.site_header = admin.site.site_title = 'Foodgram'
admin.site.unregister(Group)
admin.site.empty_value_display = '-пусто-'


class RecipeIngredientsInline(admin.TabularInline):

    model = IngredientRecipe
    extra = INLINE_EXTRA_FIELDS
    min_num = MIN_NUM
    can_delete = False


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = ('name', 'author', 'favorite_count')
    search_fields = ('name', 'author__username')
    readonly_fields = ('pub_date',)
    list_filter = ('tags',)
    autocomplete_fields = ('tags',)
    save_on_top = True
    inlines = (RecipeIngredientsInline,)

    @admin.display(description='У пользователей в избранном')
    def favorite_count(self, obj):
        return obj.recipes_in_favorite.count()


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    list_display_links = ('username',)
    readonly_fields = ('groups', 'user_permissions',)
    save_on_top = True


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('author', 'user')
    search_fields = ('^author__username',)
    list_display_links = None


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    search_fields = ('^name', 'name')
    list_display_links = ('name',)
    ordering = ('id',)
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('^name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
    search_fields = ('^user__username',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
    search_fields = ('^user__username',)
