
from django.db import models
from django.contrib.auth.models import User


class Food(models.Model):
    DIET_CHOICES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('nonveg', 'Non-vegetarian'),
    ]

    name = models.CharField(max_length=250)
    normalized_name = models.CharField(max_length=250, unique=True, editable=False)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2)
    carbohydrates_g = models.DecimalField(max_digits=8, decimal_places=2)
    fat_g = models.DecimalField(max_digits=8, decimal_places=2)
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES)
    source = models.CharField(max_length=100, default='Food Nutrition Dataset')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.normalized_name = self.name.strip().casefold()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class IndianMealOption(models.Model):
    meal_id = models.PositiveIntegerField(primary_key=True)
    category = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=50)
    total_orders = models.PositiveBigIntegerField(default=0)

    class Meta:
        ordering = ['cuisine', 'category', 'meal_id']

    def __str__(self):
        return f'{self.cuisine} {self.category} ({self.meal_id})'


class UserProfile(models.Model):
    GOAL_CHOICES = [
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight'),
    ]

    DIET_CHOICES = [
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
    ]

    ACTIVITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    activity_level = models.CharField(
        max_length=20, choices=ACTIVITY_CHOICES
    )
    goal = models.CharField(
        max_length=20, choices=GOAL_CHOICES
    )
    diet_type = models.CharField(
        max_length=20, choices=DIET_CHOICES
    )
    allergies = models.TextField(blank=True)

    def __str__(self):
        return self.user.username