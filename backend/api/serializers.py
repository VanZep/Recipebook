import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)

from recipes.models import (
    User, Recipe, Ingredient, Tag, Subscription,
    IngredientRecipe, FavoriteRecipe, ShoppingCart
)
from .validators import (
    is_not_selected_validator, only_one_selected_validator,
    min_max_value_validator, is_not_exists_objects_validator,
    user_is_author_validator
)
from .utils import (
    get_subscription_objects, get_favorite_recipe_objects,
    get_shopping_cart_objects
)


class Base64ImageField(serializers.ImageField):
    """Класс поля для изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор создания пользователей."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            user and user.is_authenticated
            and get_subscription_objects(user, author).exists()
        )


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

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes = author.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            if limit.isdigit():
                recipes = recipes[:int(limit)]
            else:
                raise serializers.ValidationError(
                    {
                        'detail':
                        'Значение recipes_limit должно быть целочисленным'
                    }
                )
        return (
            RecipeShortSerializer(
                recipes, many=True,
                context={'request': self.context.get('request')}
            ).data
        )

    def get_recipes_count(self, author):
        return author.recipes.count()


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор создания подписки."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора'
            ),
        )

    def validate_author(self, author):
        user_is_author_validator(
            self.initial_data.get('user'), author.id,
            'Нельзя подписаться на себя'
        )
        return author


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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_id(self, ingredient):
        is_not_exists_objects_validator(
            Ingredient.objects.filter(id=ingredient.id),
            'Такой ингредиент не существует'
        )
        return ingredient

    def validate_amount(self, amount):
        min_max_value_validator(amount, 'Количество')
        return amount


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор создания/изменения рецептов."""

    ingredients = IngredientRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def create_update_recipe(self, validated_data, instance=None):
        ingredients = validated_data.pop('ingredients')
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
                    ingredient=ingredient.get('id'),
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

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        ).data

    def validate_ingredients(self, ingredients):
        name = 'ингредиент'
        is_not_selected_validator(ingredients, name)
        ingredients_id_list = [item.get('id') for item in ingredients]
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
            and get_favorite_recipe_objects(user, recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.get_user()
        return (
            user and user.is_authenticated
            and get_shopping_cart_objects(user, recipe).exists()
        )


class CreteFavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания избранного рецепта."""

    class Meta:
        model = FavoriteRecipe
        fields = ('recipe', 'user')
        validators = (
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('recipe', 'user'),
                message='Данный рецепт уже находится у вас в избранном'
            ),
        )


class CreateShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в корзину покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('recipe', 'user'),
                message='Данный рецепт уже находится у вас в корзине'
            ),
        )
