"""
Команда загрузки данных CSV для модели Ingredient в БД:
python manage.py load_csv.
"""
import csv

from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Класс загрузки CSV файлов в БД."""

    def handle(self, *args, **kwargs):
        try:
            with open(
                '../data/ingredients.csv',
                'r', encoding='utf-8'
            ) as file:
                rows = csv.DictReader(file)
                Ingredient.objects.bulk_create(
                    Ingredient(**row) for row in rows
                )
                self.stdout.write(self.style.SUCCESS(
                    'Данные для модели Ingredient загружены'
                ))
        except IntegrityError as error:
            self.stdout.write(self.style.ERROR(
                f'Ошибка загрузки данных для модели Ingredient - {error}'
            ))
        except Exception as error:
            self.stdout.write(self.style.ERROR(f'Ошибка {error}'))
