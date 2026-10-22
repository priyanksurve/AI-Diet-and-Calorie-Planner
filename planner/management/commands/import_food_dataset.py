import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from planner.meal_planner import classify_diet
from planner.models import Food


REQUIRED_COLUMNS = ('food', 'Caloric Value', 'Protein', 'Carbohydrates', 'Fat')
NUTRIENT_FIELDS = {
    'calories': 'Caloric Value',
    'protein_g': 'Protein',
    'carbohydrates_g': 'Carbohydrates',
    'fat_g': 'Fat',
}


class Command(BaseCommand):
    help = 'Import nutrition values from the five Food Nutrition Dataset CSV files.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=Path,
            default=(
                settings.BASE_DIR
                / 'Food Nutrition Dataset'
                / 'FINAL FOOD DATASET'
            ),
            help='Directory containing FOOD-DATA-GROUP1.csv through GROUP5.csv.',
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        files = [source_dir / f'FOOD-DATA-GROUP{group}.csv' for group in range(1, 6)]
        missing_files = [str(path) for path in files if not path.is_file()]
        if missing_files:
            raise CommandError('Missing nutrition dataset file(s): ' + ', '.join(missing_files))

        imported = 0
        updated = 0
        with transaction.atomic():
            for path in files:
                try:
                    with path.open(encoding='utf-8-sig', newline='') as csv_file:
                        reader = csv.DictReader(csv_file)
                        missing_columns = set(REQUIRED_COLUMNS).difference(reader.fieldnames or [])
                        if missing_columns:
                            raise CommandError(
                                f'{path.name} is missing required columns: '
                                + ', '.join(sorted(missing_columns))
                            )

                        for row_number, row in enumerate(reader, start=2):
                            name = (row.get('food') or '').strip()
                            if not name:
                                raise CommandError(f'{path.name}:{row_number} has no food name.')
                            if len(name) > 250:
                                raise CommandError(f'{path.name}:{row_number} food name exceeds 250 characters.')

                            try:
                                nutrients = {
                                    field: Decimal(row[column].strip()).quantize(Decimal('0.01'))
                                    for field, column in NUTRIENT_FIELDS.items()
                                }
                            except (InvalidOperation, AttributeError):
                                raise CommandError(
                                    f'{path.name}:{row_number} has an invalid nutrition value.'
                                )

                            if any(not value.is_finite() or value < 0 for value in nutrients.values()):
                                raise CommandError(
                                    f'{path.name}:{row_number} has a negative or non-finite nutrition value.'
                                )

                            normalized_name = name.casefold()
                            _, created = Food.objects.update_or_create(
                                normalized_name=normalized_name,
                                defaults={
                                    'name': name,
                                    'diet_type': classify_diet(name),
                                    'source': path.name,
                                    **nutrients,
                                },
                            )
                            if created:
                                imported += 1
                            else:
                                updated += 1
                except UnicodeDecodeError as error:
                    raise CommandError(f'{path.name} is not valid UTF-8: {error}') from error
                except OSError as error:
                    raise CommandError(f'Could not read {path}: {error}') from error

        self.stdout.write(
            self.style.SUCCESS(
                f'Food catalog import complete: {imported} added, {updated} updated.'
            )
        )
