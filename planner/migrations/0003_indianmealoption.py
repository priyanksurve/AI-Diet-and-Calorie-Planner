from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_food'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndianMealOption',
            fields=[
                ('meal_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=100)),
                ('cuisine', models.CharField(max_length=50)),
                ('total_orders', models.PositiveBigIntegerField(default=0)),
            ],
            options={
                'ordering': ['cuisine', 'category', 'meal_id'],
            },
        ),
    ]
