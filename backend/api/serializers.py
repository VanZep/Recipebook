import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import User, Recipe, Ingredient, Tag, Subscription


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
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'title', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'title', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    recipes = RecipeSerializer(many=True)
    # is_subscribed =
    # recipes_count =

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'avatar'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    user = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='id',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='id'
    )

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора'
            )
        ]

    def validate_user(self, value):
        if self.initial_data.get('author') == value.id:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        return value
