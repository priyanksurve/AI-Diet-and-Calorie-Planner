import csv
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from planner.models import IndianMealOption


class Command(BaseCommand):
    help = 'Import Indian cuisine categories and order counts from the meal demand dataset.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=Path,
            default=settings.BASE_DIR / 'Indian Food Plan Dataset' / 'foodDemand_train',
            help='Directory containing meal_info.csv and train.csv.',
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        meal_file = source_dir / 'meal_info.csv'
        train_file = source_dir / 'train.csv'
        missing = [str(path) for path in (meal_file, train_file) if not path.is_file()]
        if missing:
            raise CommandError('Missing Indian meal dataset file(s): ' + ', '.join(missing))

        order_totals = defaultdict(int)
        try:
            with train_file.open(encoding='utf-8-sig', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                required = {'meal_id', 'num_orders'}
                missing_columns = required.difference(reader.fieldnames or [])
                if missing_columns:
                    raise CommandError(
                        f'train.csv is missing required columns: {", ".join(sorted(missing_columns))}'
                    )
                for row_number, row in enumerate(reader, start=2):
                    try:
                        meal_id = int(row['meal_id'])
                        num_orders = int(row['num_orders'])
                    except (TypeError, ValueError):
                        raise CommandError(f'train.csv:{row_number} has invalid meal/order values.')
                    if meal_id < 0 or num_orders < 0:
                        raise CommandError(f'train.csv:{row_number} has negative meal/order values.')
                    order_totals[meal_id] += num_orders

            added = 0
            updated = 0
            with transaction.atomic():
                with meal_file.open(encoding='utf-8-sig', newline='') as csv_file:
                    reader = csv.DictReader(csv_file)
                    required = {'meal_id', 'category', 'cuisine'}
                    missing_columns = required.difference(reader.fieldnames or [])
                    if missing_columns:
                        raise CommandError(
                            f'meal_info.csv is missing required columns: {", ".join(sorted(missing_columns))}'
                        )
                    for row_number, row in enumerate(reader, start=2):
                        try:
                            meal_id = int(row['meal_id'])
                        except (TypeError, ValueError):
                            raise CommandError(f'meal_info.csv:{row_number} has an invalid meal_id.')
                        category = (row['category'] or '').strip()
                        cuisine = (row['cuisine'] or '').strip()
                        if not category or not cuisine:
                            raise CommandError(
                                f'meal_info.csv:{row_number} requires both category and cuisine.'
                            )
                        _, created = IndianMealOption.objects.update_or_create(
                            meal_id=meal_id,
                            defaults={
                                'category': category,
                                'cuisine': cuisine,
                                'total_orders': order_totals.get(meal_id, 0),
                            },
                        )
                        if created:
                            added += 1
                        else:
                            updated += 1
        except UnicodeDecodeError as error:
            raise CommandError(f'Indian meal dataset is not valid UTF-8: {error}') from error
        except OSError as error:
            raise CommandError(f'Could not read Indian meal dataset: {error}') from error

        self.stdout.write(
            self.style.SUCCESS(
                f'Indian meal metadata import complete: {added} added, {updated} updated.'
            )
        )
