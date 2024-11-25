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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиентов с рецептами."""

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор записи рецептов."""

    # author = serializers.SlugRelatedField(
    #     slug_field='username', read_only=True
    # )
    # image = Base64ImageField(required=True)
    image = Base64ImageField(required=False)
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        # exclude = ('id',)
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )
        # fields = (
        #     'title', 'author', 'tag', 'description',
        #     'image', 'cooking_time'
        # )

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     print(validated_data, '|', validated_data.get('ingredients'), '|', ingredients)
    #     print()
    #     print(self.initial_data)
    #     if 'ingredients' not in self.initial_data:

    #         cat = Cat.objects.create(**validated_data)
    #         return cat
    #     else:
    #         achievements = validated_data.pop('achievements')
    #         cat = Cat.objects.create(**validated_data)
    #         for achievement in achievements:
    #             current_achievement, status = Achievement.objects.get_or_create(
    #                 **achievement)
    #             AchievementCat.objects.create(
    #                 achievement=current_achievement, cat=cat)
    #         return cat


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
