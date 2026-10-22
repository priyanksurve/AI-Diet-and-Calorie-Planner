from django.contrib import admin

from .models import Food, IndianMealOption, UserProfile


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'protein_g', 'carbohydrates_g', 'fat_g', 'diet_type')
    list_filter = ('diet_type',)
    search_fields = ('name',)


@admin.register(IndianMealOption)
class IndianMealOptionAdmin(admin.ModelAdmin):
    list_display = ('meal_id', 'category', 'cuisine', 'total_orders')
    list_filter = ('cuisine', 'category')
    search_fields = ('category', 'cuisine')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'diet_type')
    list_filter = ('goal', 'diet_type')
    search_fields = ('user__username',)
