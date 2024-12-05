import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    User, Recipe, Ingredient, Tag, IngredientRecipe, FavoriteRecipe
)
from .validators import (
    is_not_selected_validator, only_one_selected_validator,
    min_max_value_validator, is_not_exists_objects_validator,
    is_exists_objects_validator, user_is_author_validator
)
from .utils import get_favorite_recipe_objects


class Base64ImageField(serializers.ImageField):
    """Класс поля для изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        # user = self.context.get('request').user
        # return (
        #     user and user.is_authenticated
        #     and user.subscribers.filter(author=author).exists()
        # )
        return True


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов с ограниченным набором полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def create(self, validated_data):
        print()
        print(validated_data)
        print()
        # return super().create(validated_data)

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes = author.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return (
            RecipeShortSerializer(
                recipes, many=True,
                context={'request': self.context.get('request')}
            ).data
        )

    def get_recipes_count(self, author):
        return author.recipes.count()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изменения связи ингредиентов с рецептом."""

    id = serializers.IntegerField(source='ingredient.id')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_id(self, id):
        is_not_exists_objects_validator(
            Ingredient.objects.filter(id=id),
            'Такой ингредиент не существует'
        )
        return id

    def validate_amount(self, amount):
        min_max_value_validator(amount, 'Количество')
        return amount


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изменения рецептов."""

    ingredients = IngredientRecipeWriteSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def create_update_recipe(self, validated_data, instance=None):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        if instance:
            recipe = super().update(instance, validated_data)
            instance.ingredients.clear()
        else:
            recipe = super().create(validated_data)
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient.get('ingredient').get('id'),
                    amount=ingredient.get('amount')
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)
        recipe.tags.set(tags)
        return recipe

    def create(self, validated_data):
        return self.create_update_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.create_update_recipe(validated_data, instance)

    def validate_ingredients(self, ingredients):
        name = 'ингредиент'
        is_not_selected_validator(ingredients, name)
        ingredients_id_list = [
            item.get('ingredient').get('id') for item in ingredients
        ]
        only_one_selected_validator(ingredients_id_list, name)
        return ingredients

    def validate_tags(self, tags):
        name = 'тег'
        is_not_selected_validator(tags, name)
        only_one_selected_validator(tags, name)
        return tags

    def validate_cooking_time(self, time):
        min_max_value_validator(time, 'Время приготовления')
        return time


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения связи ингредиентов с рецептом."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_user(self):
        return self.context.get('request').user

    def get_is_favorited(self, recipe):
        user = self.get_user()
        return (
            user and user.is_authenticated
            and user.favorite_recipes.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.get_user()
        return (
            user and user.is_authenticated
            and user.recipes_in_cart.filter(recipe=recipe).exists()
        )


class CreteFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания избранного рецепта."""

    class Meta:
        model = FavoriteRecipe
        fields = ('recipe', 'user')

    def validate(self, attrs):
        recipe = attrs.get('recipe')
        user = attrs.get('user')
        is_exists_objects_validator(
            get_favorite_recipe_objects(user, recipe),
            'Данный рецепт уже находится у вас в избранном'
        )
        user_is_author_validator(
            user, recipe.author,
            'Нельзя добавить в избранное свой рецепт'
        )
        return attrs
