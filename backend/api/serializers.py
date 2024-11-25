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


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    # author = serializers.SlugRelatedField(
    #     slug_field='username', read_only=True
    # )
    image = Base64ImageField(required=True)
    # tag = TagSerializer(many=True)

    class Meta:
        model = Recipe
        # exclude = ('id',)
        fields = (
            'ingredient', 'tag', 'image',
            'title', 'description', 'cook_time'
        )
        # fields = (
        #     'title', 'author', 'tag', 'description',
        #     'image', 'cook_time'
        # )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    image = serializers.ImageField()
    cook_time = serializers.IntegerField()

    # class Meta:
    #     model = Recipe
    #     fields = '__all__'


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
        exclude = ('user', 'author')
        # fields = '__all__'
        # fields = (
        #     'id', 'username', 'email', 'first_name', 'last_name',
        #     'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        # )
        # read_only_fields = (
        #     'id', 'username', 'email', 'first_name', 'last_name',
        #     'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        # )

    def get_is_subscribed(self, obj):
        # print(obj.user)
        return Subscription.objects.filter(
            user=obj.user.id, author=obj.author.id
        ).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author.id)
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        # print(obj.user)
        return Recipe.objects.filter(author=obj.author.id).count()


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
