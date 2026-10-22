from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .calculations import calculate_targets
from .meal_planner import _food_roles, classify_diet, generate_weekly_plan


def catalog_food(name, calories, protein, carbohydrates, fat, diet_type='vegan'):
    return SimpleNamespace(
        name=name,
        calories=Decimal(str(calories)),
        protein_g=Decimal(str(protein)),
        carbohydrates_g=Decimal(str(carbohydrates)),
        fat_g=Decimal(str(fat)),
        diet_type=diet_type,
    )


class DietTargetCalculationTests(SimpleTestCase):
    def setUp(self):
        self.profile = {
            'age': 30,
            'gender': 'female',
            'height_cm': 165,
            'weight_kg': 65,
            'activity_level': 'moderate',
        }

    def test_calculates_maintenance_targets_and_macros(self):
        targets = calculate_targets(goal='maintain', **self.profile)

        self.assertEqual(targets.bmr, 1370)
        self.assertEqual(targets.maintenance_calories, 2124)
        self.assertEqual(targets.daily_calories, targets.maintenance_calories)
        self.assertEqual(targets.protein_g, 104)
        self.assertEqual(targets.fat_g, 52)
        self.assertGreater(targets.carbohydrates_g, 0)

    def test_weight_loss_and_gain_adjust_maintenance_calories(self):
        maintenance = calculate_targets(goal='maintain', **self.profile)
        weight_loss = calculate_targets(goal='lose', **self.profile)
        weight_gain = calculate_targets(goal='gain', **self.profile)

        self.assertLess(weight_loss.daily_calories, maintenance.daily_calories)
        self.assertGreater(weight_gain.daily_calories, maintenance.daily_calories)
        self.assertLessEqual(maintenance.daily_calories - weight_loss.daily_calories, 500)
        self.assertLessEqual(weight_gain.daily_calories - maintenance.daily_calories, 300)

    def test_rejects_unknown_calculation_options(self):
        profile = self.profile.copy()
        profile['gender'] = 'unknown'

        with self.assertRaises(ValueError):
            calculate_targets(goal='maintain', **profile)

    def test_creates_seven_days_with_four_database_nutrition_meals(self):
        catalog = [
            catalog_food('oats', 150, 5, 27, 3),
            catalog_food('banana', 100, 1, 27, 0.3),
            catalog_food('apple', 95, 0.5, 25, 0.3),
            catalog_food('lentils', 115, 9, 20, 0.4),
            catalog_food('rice', 130, 2.7, 28, 0.3),
            catalog_food('spinach', 23, 3, 4, 0.4),
            catalog_food('chickpeas', 164, 9, 27, 2.6),
        ]

        indian_options = [
            SimpleNamespace(meal_id=1109, category='Rice Bowl', cuisine='Indian', total_orders=300),
            SimpleNamespace(meal_id=1902, category='Biryani', cuisine='Indian', total_orders=200),
        ]
        plan = generate_weekly_plan(catalog, 2000, 'vegan', indian_options=indian_options)

        self.assertEqual(len(plan), 7)
        self.assertEqual([meal['key'] for meal in plan[0]['meals']], [
            'breakfast', 'lunch', 'snack', 'dinner',
        ])
        for day in plan:
            self.assertGreater(day['calories'], 0)
            self.assertEqual(len(day['meals']), 4)
            self.assertIn(
                day['meals'][1]['menu_inspiration']['category'],
                {'Rice Bowl', 'Biryani'},
            )
            self.assertIn(
                day['meals'][3]['menu_inspiration']['category'],
                {'Rice Bowl', 'Biryani'},
            )
            self.assertIsNone(day['meals'][0]['menu_inspiration'])
        self.assertEqual(plan[0]['meals'][1]['menu_inspiration']['category'], 'Rice Bowl')

    def test_excludes_foods_that_conflict_with_diet_or_allergies(self):
        catalog = [
            catalog_food('oats', 150, 5, 27, 3),
            catalog_food('apple', 95, 0.5, 25, 0.3),
            catalog_food('peanuts', 160, 7, 5, 14),
            catalog_food('yogurt', 120, 10, 8, 4, 'vegetarian'),
            catalog_food('chicken breast', 165, 31, 0, 4, 'nonveg'),
        ]

        plan = generate_weekly_plan(catalog, 2000, 'vegan', 'peanuts, dairy')
        planned_names = {
            item['food'].name
            for day in plan
            for meal in day['meals']
            for item in meal['foods']
        }

        self.assertNotIn('peanuts', planned_names)
        self.assertNotIn('yogurt', planned_names)
        self.assertNotIn('chicken breast', planned_names)

    def test_avoids_processed_bars_and_fruit_bread_as_fresh_food(self):
        catalog = [
            catalog_food('banana bread', 230, 4, 43, 5),
            catalog_food('banana chips', 519, 2.3, 58, 33),
            catalog_food('apple', 95, 0.5, 25, 0.3),
            catalog_food('almonds', 164, 6, 6, 14, 'vegan'),
            catalog_food('brown rice cooked', 218, 5, 46, 2),
            catalog_food('lentils cooked', 230, 18, 40, 1),
            catalog_food('spinach cooked', 41, 5, 7, 0.5),
        ]

        plan = generate_weekly_plan(catalog, 2000, 'vegan')
        planned_names = {
            item['food'].name
            for day in plan
            for meal in day['meals']
            for item in meal['foods']
        }

        self.assertNotIn('banana bread', planned_names)
        self.assertNotIn('banana chips', planned_names)

    def test_classifies_eggplant_as_vegan_not_egg_based(self):
        self.assertEqual(classify_diet('eggplant'), 'vegan')

    def test_classifies_indian_foods_and_animal_products(self):
        self.assertEqual(classify_diet('chaptti roti indian bread'), 'vegan')
        self.assertEqual(classify_diet('lentils cooked'), 'vegan')
        self.assertEqual(classify_diet('paneer'), 'vegetarian')
        self.assertEqual(classify_diet('chicken breast'), 'nonveg')
        self.assertEqual(classify_diet('pasta with meatballs in tomato sauce'), 'nonveg')
        self.assertEqual(classify_diet('clam tomato juice'), 'nonveg')
        self.assertEqual(classify_diet('chocolate milkshake'), 'vegetarian')
        self.assertNotIn('fruit', _food_roles(catalog_food('banana pepper', 30, 1, 5, 0.2)))


class CalculatorViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='planner-member', password='Test-password-123!')
        self.client.force_login(self.user)
        self.form_data = {
            'age': 30,
            'gender': 'female',
            'height_cm': 165,
            'weight_kg': 65,
            'activity_level': 'moderate',
            'goal': 'maintain',
            'diet_type': 'veg',
            'allergies': '',
        }

    def test_home_is_a_public_landing_page(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Diet')
        self.assertContains(response, 'Personalized 7-Day Meal Plans')
        self.assertContains(response, 'healthy-choices-happy-progress.png')
        self.assertContains(response, 'Open planner')

    def test_valid_submission_displays_personalized_targets(self):
        with (
            patch('planner.views.Food.objects.all', return_value=[]),
            patch('planner.views.IndianMealOption.objects.filter', return_value=[]),
        ):
            response = self.client.post('/calculator/', self.form_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/plan/', 302)])
        self.assertContains(response, '2124')
        self.assertContains(response, '1370')

    def test_valid_submission_renders_a_week_of_database_foods(self):
        catalog = [
            catalog_food('oats', 150, 5, 27, 3),
            catalog_food('banana', 100, 1, 27, 0.3),
            catalog_food('apple', 95, 0.5, 25, 0.3),
            catalog_food('lentils', 115, 9, 20, 0.4),
            catalog_food('rice', 130, 2.7, 28, 0.3),
            catalog_food('spinach', 23, 3, 4, 0.4),
            catalog_food('chickpeas', 164, 9, 27, 2.6),
        ]
        indian_options = [
            SimpleNamespace(meal_id=1109, category='Rice Bowl', cuisine='Indian', total_orders=300),
            SimpleNamespace(meal_id=1902, category='Biryani', cuisine='Indian', total_orders=200),
        ]
        with (
            patch('planner.views.Food.objects.all', return_value=catalog),
            patch('planner.views.IndianMealOption.objects.filter', return_value=indian_options),
        ):
            response = self.client.post('/calculator/', self.form_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/plan/', 302)])
        self.assertContains(response, 'Your 7-day meal plan')
        self.assertEqual(response.content.count(b'<summary class="day-summary">'), 7)
        self.assertEqual(response.content.count(b'<h3 class="h5 fw-bold mb-1">'), 28)
        self.assertContains(response, 'oats')
        self.assertContains(response, 'Indian menu inspiration: Rice Bowl')
        self.assertContains(response, 'Food Nutrition Dataset')
        self.assertContains(response, 'Indian Food Plan Dataset')

    def test_plan_page_can_be_reloaded_after_redirect(self):
        with (
            patch('planner.views.Food.objects.all', return_value=[]),
            patch('planner.views.IndianMealOption.objects.filter', return_value=[]),
        ):
            submission = self.client.post('/calculator/', self.form_data)
            response = self.client.get(submission['Location'])

        self.assertEqual(submission.status_code, 302)
        self.assertEqual(submission['Location'], '/plan/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your 7-day meal plan')

    def test_empty_catalog_explains_how_to_import_foods(self):
        with (
            patch('planner.views.Food.objects.all', return_value=[]),
            patch('planner.views.IndianMealOption.objects.filter', return_value=[]),
        ):
            response = self.client.post('/calculator/', self.form_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'import_food_dataset')

    def test_plan_page_without_calculator_submission_returns_to_form(self):
        response = self.client.get('/plan/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/calculator/')

    def test_rejects_underage_profile(self):
        response = self.client.post('/calculator/', {**self.form_data, 'age': 17})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/calculator/')
        self.assertContains(response, 'Ensure this value is greater than or equal to 18.')


class AuthenticationFlowTests(TestCase):
    def test_homepage_is_accessible_before_login(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create account')
        self.assertContains(response, 'AI Diet')
        self.assertContains(response, 'Personalized 7-Day Meal Plans')
        self.assertContains(response, 'Log in')

    def test_anonymous_members_are_sent_to_login_for_calculator_and_plan(self):
        for path in ('/calculator/', '/plan/'):
            response = self.client.get(path)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], f'/login/?next={path}')

    def test_registration_creates_account_and_logs_member_in(self):
        response = self.client.post(
            '/register/',
            {
                'username': 'new-member',
                'email': 'member@example.com',
                'password1': 'Strong-password-123!',
                'password2': 'Strong-password-123!',
            },
        )

        self.assertRedirects(response, '/calculator/', fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='new-member').exists())
        calculator_response = self.client.get('/calculator/')
        self.assertEqual(calculator_response.status_code, 200)

    def test_invalid_registration_keeps_member_on_registration_page(self):
        response = self.client.post(
            '/register/',
            {
                'username': 'new-member',
                'email': 'member@example.com',
                'password1': 'short',
                'password2': 'different',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
        self.assertFalse(User.objects.filter(username='new-member').exists())

    def test_login_then_logout_returns_to_public_home(self):
        User.objects.create_user(username='existing-member', password='Strong-password-123!')

        login_response = self.client.post(
            '/login/',
            {'username': 'existing-member', 'password': 'Strong-password-123!'},
        )

        self.assertRedirects(login_response, '/calculator/', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/calculator/').status_code, 200)
        logout_response = self.client.post('/logout/')
        self.assertRedirects(logout_response, '/', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/calculator/').status_code, 302)
