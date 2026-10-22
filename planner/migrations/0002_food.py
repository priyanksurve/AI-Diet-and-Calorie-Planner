from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('normalized_name', models.CharField(editable=False, max_length=250, unique=True)),
                ('calories', models.DecimalField(decimal_places=2, max_digits=8)),
                ('protein_g', models.DecimalField(decimal_places=2, max_digits=8)),
                ('carbohydrates_g', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fat_g', models.DecimalField(decimal_places=2, max_digits=8)),
                ('diet_type', models.CharField(choices=[('vegan', 'Vegan'), ('vegetarian', 'Vegetarian'), ('nonveg', 'Non-vegetarian')], max_length=20)),
                ('source', models.CharField(default='Food Nutrition Dataset', max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
