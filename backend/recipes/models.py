from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.validators import ASCIIUsernameValidator

from core.models import NameModel
from core.constants import (
    USER_CHARFIELD_MAX_LENGTH, EMAILFIELD_MAX_LENGTH,
    CHARFIELD_MAX_LENGTH, SLUGFIELD_MAX_LENGTH,
    MIN_VALUE, MAX_VALUE
)


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=USER_CHARFIELD_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Юзернейм',
        validators=(ASCIIUsernameValidator(),)
    )
    email = models.EmailField(
        max_length=EMAILFIELD_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False,
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
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers',
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
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_subscribers_author'
            )
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
        ordering = ('name',)

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
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

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
                MIN_VALUE,
                f'Минимальное время приготовления {MIN_VALUE} (мин).'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Максимальное время приготовления {MAX_VALUE} (мин).'
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
        related_name='recipes_in_favorite',
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
                name='unique_recipe_in_favorite_user'
            ),
        )

    def __str__(self):
        return f'Избранный {self.recipe} для {self.user}'


class ShoppingCart(models.Model):
    """Модель корзины."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_in_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_in_shopping_cart_user'
            ),
        )

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'


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
                MIN_VALUE,
                f'Минимальное количество {MIN_VALUE}.'
            ),
            MaxValueValidator(
                MAX_VALUE,
                f'Максимальное количество {MAX_VALUE}.'
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
        return f'{self.ingredient} для {self.recipe}'
