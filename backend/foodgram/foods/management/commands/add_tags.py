import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import Tag

PROJECT_DIR = Path(settings.BASE_DIR).resolve().joinpath('data')
FILE_TO_OPEN = PROJECT_DIR / 'tags.csv'


class Command(BaseCommand):
    help = 'Импорт тегов'

    def handle(self, **kwargs):
        with open(
            FILE_TO_OPEN, 'r', encoding='UTF-8'
        ) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                Tag.objects.get_or_create(
                    name=row[0],
                    color=row[1],
                    slug=row[2]
                )
