import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    User, Recipe, Ingredient, IngredientRecipe, Tag, Subscription
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

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
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

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe_id=recipe.id,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            )
        recipe.tags.set(tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe_id=instance.id,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            )
        instance.tags.set(tags)
        # print()
        # print(tags)
        # print()
        # instance.ingredients.set(*ingredients)

        return instance


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиентов с рецептами."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    # name = serializers.ReadOnlyField(source='ingredient.name')
    # measurement_unit = serializers.ReadOnlyField(
    #     source='ingredient.measurement_unit'
    # )

    # id = serializers.ReadOnlyField(source='ingredient_id')#, source='ingredient')
    # id = serializers.PrimaryKeyRelatedField(queryset=IngredientRecipe.objects.all())
    # id = serializers.IntegerField(source='ingredient.id')
    # amount = serializers.IntegerField(source='ingredient_recipes')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    # tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )
        # fields = (
        #     'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        # )


# class IngredientForRecipeSerializer(serializers.ModelSerializer):
#     id = serializers.ReadOnlyField(source='ingredient.id')
#     name = serializers.ReadOnlyField(source='ingredient.name')
#     measurement_unit = serializers.ReadOnlyField(
#         source='ingredient.measurement_unit'
#     )

#     class Meta:
#         model = IngredientRecipe
#         fields = [
#             'id',
#             'name',
#             'measurement_unit',
#             'amount',
#         ]


# class RecipeSerializer(serializers.ModelSerializer):
#     author = UserSerializer(read_only=True)
#     tags = TagSerializer(many=True, read_only=True)
#     ingredients = IngredientForRecipeSerializer(
#         source='recipeingredient_set',
#         many=True,
#         read_only=True,
#     )

    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    # image = Base64ImageField()

    # class Meta:
    #     model = Recipe
    #     fields = [
    #         'id',
    #         'tags',
    #         'author',
    #         'ingredients',
    #         # 'is_favorited',
    #         # 'is_in_shopping_cart',
    #         'name',
    #         'image',
    #         'text',
    #         'cooking_time',
    #     ]

    # def get_is_in_shopping_cart(self, obj):
    #     request = self.context.get('request')
    #     user = request.user
    #     if not user or user.is_anonymous:
    #         return False
    #     return RecipeInShoppingCart.objects.filter(
    #         recipe=obj,
    #         user=user
    #     ).exists()

    # def get_is_favorited(self, obj):
    #     request = self.context.get('request')
    #     user = request.user
    #     if not user or user.is_anonymous:
    #         return False
    #     queryset = FavoriteRecipe.objects.all()
    #     return queryset.filter(recipe=obj, user=user).exists()


# class RecipeWriteSerializer(serializers.ModelSerializer):
#     ingredients = IngredientRecipeSerializer(
#         many=True,
#     )
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(),
#         many=True,
#     )

#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = [
#             'ingredients',
#             'tags',
#             'image',
#             'name',
#             'text',
#             'cooking_time',
#         ]

#     def create_related_ingredients(self, recipe, ingredients_data):
#         recipe_ingredients = []
#         for ingredient_data in ingredients_data:
#             recipe_ingredient = IngredientRecipe(
#                 recipe=recipe,
#                 ingredient_id=ingredient_data['ingredient']['id'],
#                 amount=ingredient_data['amount'],
#             )
#             recipe_ingredients.append(recipe_ingredient)
#         IngredientRecipe.objects.bulk_create(recipe_ingredients)

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')

#         instance = super().create(validated_data)

#         self.create_related_ingredients(instance, ingredients_data)
#         instance.tags.set(tags_data)

#         return instance

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     if not ingredients:
    #         raise serializers.ValidationError(
    #             "Ingredients field cannot be empty.",
    #         )
    #     tags = validated_data.pop('tags')
    #     recipes = Recipe.objects.create(**validated_data)
    #     recipes.save()
    #     for ingredient in ingredients:
    #         current_ingredient = ingredient.get('id')
    #         amount = ingredient.get('amount')
    #         recipes.ingredients.add(
    #             current_ingredient,
    #             through_defaults={
    #                 'amount': amount,
    #             }
    #         )

    #     for tag in tags:
    #         recipes.tags.add(tag)

    #     return recipes


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения рецептов."""

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов с ограниченным набором полей."""

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
    avatar = serializers.CharField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        # fields = '__all__'
        # read_only_fields = (
        #     'id', 'username', 'email', 'first_name', 'last_name',
        #     'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        # )

    def get_recipe_objects(self, obj):
        return Recipe.objects.filter(author=obj.author.id)

    def get_is_subscribed(self, obj):
        # print(obj.user)
        return Subscription.objects.filter(
            user=obj.user.id, author=obj.author.id
        ).exists()

    def get_recipes(self, obj):
        serializer = RecipeShortSerializer(
            self.get_recipe_objects(obj), many=True
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
