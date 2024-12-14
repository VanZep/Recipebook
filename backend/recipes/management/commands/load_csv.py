"""
Команда загрузки CSV файлов в БД:
python manage.py load_csv.
"""
import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Recipe, Tag


class Command(BaseCommand):
    """Класс загрузки CSV файлов в БД."""

    def handle(self, *args, **kwargs):
        try:
            with open(f'{settings.BASE_DIR}/data/recipetag.csv') as csv_file:
                rows = csv.DictReader(csv_file)
                for row in rows:
                    Recipe(pk=row['recipe_id']).tags.add(Tag(pk=row['tag_id']))
                self.stdout.write(
                    self.style.SUCCESS('Данные модели RecipeTag загружены')
                )
        except Exception as error:
            self.stdout.write(self.style.ERROR(f'Ошибка {error}'))
