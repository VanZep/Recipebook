from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import TitleModel
from core.constants import (
    USER_CHARFIELD_MAX_LENGTH, EMAILFIELD_MAX_LENGTH,
    CHARFIELD_MAX_LENGTH, SLUGFIELD_MAX_LENGTH
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
        default=False
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'email')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Tag(TitleModel):
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
        return self.title


class Ingredient(TitleModel):
    """Модель ингредиентов."""

    measurement_unit = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.title


class Recipe(TitleModel):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    tag = models.ManyToManyField(Tag)
    description = models.TextField(
        verbose_name='Описание'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    cook_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-title',)

    def __str__(self):
        return self.title
