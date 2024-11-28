from django.db import models
from django.db.models.constraints import CheckConstraint
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

from core.models import NameModel
from core.constants import (
    USER_CHARFIELD_MAX_LENGTH, EMAILFIELD_MAX_LENGTH,
    CHARFIELD_MAX_LENGTH, SLUGFIELD_MAX_LENGTH,
    MIN_TIME, MIN_AMOUNT
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=USER_CHARFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Юзернейм',
    )
    email = models.EmailField(
        max_length=EMAILFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        max_length=USER_CHARFIELD_MAX_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_CHARFIELD_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=USER_CHARFIELD_MAX_LENGTH,
        verbose_name='Пароль'
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='Флаг подписки'
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            ),
            # CheckConstraint(
            #     check=~models.Q(author=models.F('user')),
            #     name='author_not_equals_user'
            # )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(NameModel):
    """Модель тегов."""

    slug = models.SlugField(
        max_length=SLUGFIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(NameModel):
    """Модель ингредиентов."""

    measurement_unit = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        # ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(NameModel):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_TIME,
                f'Минимальное время приготовления {MIN_TIME} минута.'
            ),
        ),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class FavoriteRecipe(models.Model):
    """Модель избранных рецептов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorites',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            ),
        )

    def __str__(self):
        return f'Избранный рецепт - {self.recipe} для {self.user}'


class IngredientRecipe(models.Model):
    """Модель связи ингредиентов с рецептами."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                MIN_AMOUNT,
                f'Минимальное количество {MIN_AMOUNT}.'
            ),
        ),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'ингредтент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_recipe'
            ),
        )

    def __str__(self):
        return f'Ингредиент - {self.ingredient} для рецепта - {self.recipe}'
