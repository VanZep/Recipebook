import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    User, Recipe, Ingredient, IngredientRecipe, Tag,
    Subscription, FavoriteRecipe, ShoppingCart
)


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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return bool(
            user and user.is_authenticated
            and user.subscribers.filter(author=obj).exists()
        )


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
            IngredientRecipe.objects.filter(recipe=instance).delete()
        else:
            recipe = super().create(validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe_id=recipe.id,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)
        # print()
        # print(tags)
        # print()
        # instance.ingredients.set(*ingredients)
        # recipes.ingredients.add(
        #     current_ingredient,
        #     through_defaults={'amount': amount}
        # )
        return recipe

    def create(self, validated_data):
        return self.create_update_recipe(validated_data)

    def update(self, instance, validated_data):
        return self.create_update_recipe(validated_data, instance)


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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов с ограниченным набором полей."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецептов в избранное/корзину."""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    email = serializers.EmailField(source='author.email')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        # fields = '__all__'
        # read_only_fields = (
        #     'email', 'id', 'username', 'first_name', 'last_name',
        #     'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        # )

    def get_recipe_objects(self, obj):
        # print(obj)
        return Recipe.objects.filter(author=obj.author)

    def get_is_subscribed(self, obj):
        # print(obj)
        # return Subscription.objects.filter(
        #     user=obj.user.id, author=obj.author.id
        # ).exists()
        # print(obj.user.subscribers.filter(author=obj.author))
        return obj.user.subscribers.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        # print()
        # print(obj.author.recipes.all())
        # print()
        serializer = RecipeShortSerializer(
            self.get_recipe_objects(obj), many=True,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    # def get_recipes(self, obj):
    #     recipes = Recipe.objects.filter(author=obj.author.id)
    #     serializer = RecipeShortSerializer(recipes, many=True)
    #     return serializer.data

    def get_recipes_count(self, obj):
        # print(obj.user)
        return self.get_recipe_objects(obj).count()


# class SubscribeSerializer(serializers.ModelSerializer):
#     """Сериализатор подписок."""

#     user = serializers.SlugRelatedField(
#         queryset=User.objects.all(), slug_field='id',
#         default=serializers.CurrentUserDefault()
#     )
#     author = serializers.SlugRelatedField(
#         queryset=User.objects.all(), slug_field='id'
#     )

#     class Meta:
#         model = Subscription
#         fields = ('user', 'author')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=('user', 'author'),
#                 message='Вы уже подписаны на данного автора'
#             )
#         ]

#     def validate_user(self, value):
#         if self.initial_data.get('author') == value.id:
#             raise serializers.ValidationError('Нельзя подписаться на себя')
#         return value
