"""
Команда загрузки Json файлов в БД:
python manage.py load_json.
"""
import json

from django.db.utils import IntegrityError
from django.core.management import BaseCommand

from foodgram_backend.settings import BASE_DIR
from recipes.models import User, Ingredient, Tag, Recipe, IngredientRecipe

MODELS_JSONFILES = {
    User: 'users.json', Ingredient: 'ingredients.json', Tag: 'tags.json',
    Recipe: 'recipes.json', IngredientRecipe: 'ingredientrecipe.json'
}


class Command(BaseCommand):
    """Класс загрузки Json файлов в БД."""

    def handle(self, *args, **kwargs):
        success_message_list = []
        warning_message_list = []
        for model, json_file in MODELS_JSONFILES.items():
            model_name = model.__name__
            try:
                with open(
                    f'{BASE_DIR}/data/{json_file}',
                    'r', encoding='utf-8'
                ) as file:
                    data = json.loads(file.read())
                    not_create_count = 0
                    for i, item in enumerate(data):
                        if model == User:
                            password = item.pop('password')
                            user = User.objects.filter(**item)
                            if not user.exists():
                                User.objects.create_user(
                                    **item, password=password
                                )
                            else:
                                not_create_count += 1
                        else:
                            _, is_create = model.objects.get_or_create(**item)
                            if not is_create:
                                not_create_count += 1
                    success_message_list.append(
                        f'Загружено {i + 1 - not_create_count} '
                        f'объектов для модели {model_name}'
                    )
                    warning_message_list.append(
                        f'Не загружено {not_create_count} '
                        f'объектов для модели {model_name}'
                    )
            except IntegrityError as error:
                self.stdout.write(self.style.ERROR(
                    f'Ошибка загрузки данных модели {model_name} - {error}'
                ))
            except Exception as error:
                self.stdout.write(self.style.ERROR(f'Ошибка {error}'))

        [
            self.stdout.write(
                self.style.SUCCESS(i)
            ) for i in success_message_list
        ]
        [
            self.stdout.write(
                self.style.WARNING(i)
            ) for i in warning_message_list
        ]
