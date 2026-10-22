import re
from decimal import Decimal, ROUND_HALF_UP


MEALS = [
    {
        'key': 'breakfast',
        'name': 'Breakfast',
        'time': '8:00 AM',
        'calorie_share': Decimal('0.25'),
        'roles': [('grain', Decimal('0.50')), ('protein', Decimal('0.25')), ('fruit', Decimal('0.25'))],
        'explanation': 'A mix of an energy-giving staple with protein and fruit, selected from the food catalog.',
    },
    {
        'key': 'lunch',
        'name': 'Lunch',
        'time': '1:00 PM',
        'calorie_share': Decimal('0.35'),
        'roles': [('grain', Decimal('0.40')), ('protein', Decimal('0.35')), ('vegetable', Decimal('0.25'))],
        'explanation': 'A balanced main meal combining a staple, a protein source, and vegetables where available.',
    },
    {
        'key': 'snack',
        'name': 'Evening snack',
        'time': '4:30 PM',
        'calorie_share': Decimal('0.10'),
        'roles': [('fruit', Decimal('0.50')), ('protein', Decimal('0.50'))],
        'explanation': 'A smaller snack pairing fruit with a protein-rich catalog item where available.',
    },
    {
        'key': 'dinner',
        'name': 'Dinner',
        'time': '7:30 PM',
        'calorie_share': Decimal('0.30'),
        'roles': [('grain', Decimal('0.40')), ('protein', Decimal('0.35')), ('vegetable', Decimal('0.25'))],
        'explanation': 'A varied main meal assembled from database foods, with portions scaled toward your daily target.',
    },
]

ROLE_TERMS = {
    'grain': (
        'rice', 'bread', 'roti', 'chapati', 'wheat', 'oat', 'cereal', 'pasta',
        'noodle', 'potato', 'potatoes', 'corn', 'quinoa', 'barley', 'millet', 'tortilla',
    ),
    'protein': (
        'chicken', 'turkey', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp',
        'egg', 'tofu', 'tempeh', 'lentil', 'lentils', 'bean', 'beans', 'chickpea',
        'chickpeas', 'pea', 'peas', 'yogurt', 'yoghurt', 'cheese', 'milk',
        'curd', 'paneer', 'nut', 'nuts', 'peanut', 'peanuts', 'almond',
        'almonds', 'cashew', 'cashews', 'walnut', 'walnuts',
    ),
    'vegetable': (
        'vegetable', 'spinach', 'tomato', 'tomatoes', 'broccoli', 'carrot', 'lettuce',
        'cabbage', 'pepper', 'cucumber', 'onion', 'cauliflower', 'zucchini',
        'mushroom', 'kale', 'pumpkin', 'salad', 'eggplant', 'aubergine',
    ),
    'fruit': (
        'fruit',         'apple', 'banana', 'orange', 'berry', 'berries', 'strawberry', 'strawberries', 'blueberry', 'blueberries', 'mango',
        'grape', 'pear', 'peach', 'melon', 'pineapple', 'papaya', 'date',
    ),
}
INDIAN_ROLE_PREFERENCES = {
    'grain': (
        'brown rice cooked', 'white rice cooked', 'rice cooked', 'chaptti roti',
        'roti', 'basmati rice',
    ),
    'protein': (
        'lentils cooked', 'chickpeas cooked', 'chickpeas canned',
        'chickpea flour', 'paneer', 'tofu', 'chicken breast cooked',
    ),
    'vegetable': (
        'spinach cooked', 'spinach', 'carrot cooked', 'green beans cooked',
        'cauliflower cooked', 'tomato', 'cucumber',
    ),
    'fruit': ('banana', 'mango', 'apple', 'orange', 'papaya'),
}
DEFAULT_ROLE_PREFERENCES = {
    'grain': (
        'oats', 'brown rice cooked', 'white rice cooked', 'oatmeal',
        'whole wheat bread', 'potato baked', 'rice cooked',
    ),
    'protein': (
        'lentils cooked', 'chickpeas cooked', 'beans cooked', 'tofu',
        'greek yogurt', 'yogurt plain', 'chicken breast cooked',
    ),
    'vegetable': (
        'spinach cooked', 'broccoli cooked', 'carrot cooked', 'green beans cooked',
        'tomato', 'cucumber', 'spinach raw',
    ),
    'fruit': ('banana', 'apple', 'orange', 'strawberry', 'blueberry', 'mango'),
}
MEAL_ROLE_PREFERENCES = {
    'breakfast': {
        'grain': ('oats', 'oatmeal', 'porridge', 'whole wheat bread', 'rice cooked'),
        'protein': ('greek yogurt', 'yogurt plain', 'egg cooked', 'tofu', 'beans cooked'),
    },
    'snack': {
        'protein': ('nuts', 'peanut', 'greek yogurt', 'yogurt plain', 'tofu', 'chickpeas cooked'),
    },
}

AVOID_TERMS = (
    'oil', 'syrup', 'sugar', 'candy', 'chocolate', 'soda', 'soft drink',
    'alcohol', 'wine', 'beer', 'sauce', 'dressing', 'shortening', 'cake',
    'pastry', 'cookie', 'biscuit', 'donut', 'doughnut', 'ice cream', 'bar',
    'butter', 'milkshake', 'banana bread', 'chips', 'pie', 'coated',
    'muffin', 'parfait',
)

ANIMAL_TERMS = (
    'beef', 'pork', 'chicken', 'turkey', 'fish', 'salmon', 'tuna', 'shrimp',
    'prawn', 'seafood', 'meat', 'lamb', 'mutton', 'bacon', 'sausage', 'ham',
    'duck', 'crab', 'lobster', 'anchovy', 'gelatin', 'meatball', 'sardine',
    'steak', 'veal', 'venison', 'pepperoni', 'frankfurter', 'frank', 'prosciutto',
    'clam', 'oyster', 'mussel', 'scallop', 'squid', 'octopus', 'eel', 'cod',
    'trout', 'haddock', 'mackerel',
)
ANIMAL_PRODUCT_TERMS = (
    'egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt', 'whey',
    'casein', 'honey', 'ghee',
)
PLANT_MILK_TERMS = ('soy milk', 'almond milk', 'oat milk', 'coconut milk', 'rice milk')
PLANT_FOOD_TERMS = (
    'fruit', 'apple', 'banana', 'orange', 'berry', 'berries', 'strawberry',
    'blueberry', 'mango', 'grape', 'pear', 'peach', 'melon', 'pineapple',
    'papaya', 'date', 'vegetable', 'spinach', 'tomato', 'broccoli', 'carrot',
    'lettuce', 'cabbage', 'pepper', 'cucumber', 'onion', 'cauliflower',
    'zucchini', 'mushroom', 'kale', 'pumpkin', 'salad', 'eggplant',
    'aubergine', 'rice', 'oat', 'corn', 'quinoa', 'barley', 'millet',
    'lentil', 'bean', 'chickpea', 'pea', 'tofu', 'tempeh', 'soy', 'almond',
    'cashew', 'hazelnut', 'pecan', 'pistachio', 'walnut', 'peanut',
    'potato', 'sweet potato', 'olive', 'avocado', 'roti', 'chaptti',
)
ALLERGEN_ALIASES = {
    'dairy': ('milk', 'cheese', 'butter', 'cream', 'yogurt', 'yoghurt', 'whey', 'casein', 'paneer'),
    'nuts': ('almond', 'cashew', 'hazelnut', 'pecan', 'pistachio', 'walnut', 'peanut'),
    'tree nuts': ('almond', 'cashew', 'hazelnut', 'pecan', 'pistachio', 'walnut'),
    'gluten': ('wheat', 'barley', 'rye', 'gluten'),
    'shellfish': ('shrimp', 'prawn', 'crab', 'lobster', 'shellfish'),
}


def classify_diet(name):
    normalized = name.casefold()
    if any(_matches_term(normalized, term) for term in ANIMAL_TERMS):
        return 'nonveg'
    if any(_matches_term(normalized, term) for term in ANIMAL_PRODUCT_TERMS) and not any(
        _matches_term(normalized, term) for term in PLANT_MILK_TERMS
    ):
        return 'vegetarian'
    if any(_matches_term(normalized, term) for term in PLANT_FOOD_TERMS):
        return 'vegan'
    return 'vegetarian'


def _matches_term(name, term):
    term = term.casefold()
    if term.endswith('y'):
        term_pattern = re.escape(term[:-1]) + r'(?:y|ies)'
    elif term.endswith(('s', 'x', 'ch', 'sh')):
        term_pattern = re.escape(term) + r'(?:es)?'
    else:
        term_pattern = re.escape(term) + r's?'
    return re.search(r'(?<!\w)' + term_pattern + r'(?!\w)', name.casefold()) is not None


def _eligible_foods(food_catalog, diet_type, allergies):
    allergy_terms = set()
    for term in re.split(r'[,;]', allergies or ''):
        normalized_term = term.strip().casefold()
        if normalized_term:
            allergy_terms.add(normalized_term)
            allergy_terms.update(ALLERGEN_ALIASES.get(normalized_term, ()))
    eligible = []
    for food in food_catalog:
        name = food.name.casefold()
        is_vegetarian = diet_type in {'veg', 'vegetarian'}
        if food.diet_type == 'nonveg' and (is_vegetarian or diet_type == 'vegan'):
            continue
        if food.diet_type == 'vegetarian' and diet_type == 'vegan':
            continue
        if any(_matches_term(name, term) for term in allergy_terms):
            continue
        if any(_matches_term(name, term) for term in AVOID_TERMS):
            continue
        if Decimal(food.calories) <= 0:
            continue
        eligible.append(food)
    return eligible


def _food_roles(food):
    name = food.name.casefold()
    roles = {
        role for role, terms in ROLE_TERMS.items()
        if any(_matches_term(name, term) for term in terms)
    }
    if 'banana pepper' in name:
        roles.discard('fruit')
    return roles


def _portion_for(calories, food_calories):
    portion = (
        (calories / Decimal(food_calories) * 4)
        .quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        / 4
    )
    return max(Decimal('0.25'), min(portion, Decimal('5.00')))


def _choose_foods(catalog, meal, day_index, used_names, indian_inspiration):
    chosen = []
    indian_style = indian_inspiration is not None
    for role, _ in meal['roles']:
        matches = [
            food for food in catalog
            if role in _food_roles(food)
            and food.name not in used_names
            and all(food.name != existing.name for existing, _ in chosen)
        ]
        if not matches:
            matches = [food for food in catalog if role in _food_roles(food)]
        if matches:
            preferences = INDIAN_ROLE_PREFERENCES[role] if indian_style else (
                MEAL_ROLE_PREFERENCES.get(meal['key'], {}).get(
                    role,
                    DEFAULT_ROLE_PREFERENCES[role],
                )
            )
            matches.sort(
                key=lambda food: (
                    next(
                        (
                            index for index, term in enumerate(preferences)
                            if _matches_term(food.name, term)
                        ),
                        len(preferences),
                    ),
                    food.name.casefold(),
                )
            )
            chosen.append((matches[day_index % len(matches)], role))
            continue

        fallback = [
            food for food in catalog
            if food.name not in used_names
            and all(food.name != existing.name for existing, _ in chosen)
        ]
        if not fallback:
            fallback = catalog
        if fallback:
            fallback.sort(key=lambda food: food.name.casefold())
            chosen.append((fallback[day_index % len(fallback)], role))
    return chosen


def _indian_menu_inspiration(indian_options, day_index, meal_key):
    if meal_key not in {'lunch', 'dinner'}:
        return None

    main_meals = [
        option for option in indian_options
        if option.cuisine.casefold() == 'indian'
        and option.category.casefold() in {'biryani', 'rice bowl'}
    ]
    if not main_meals:
        return None

    main_meals.sort(
        key=lambda option: (
            -option.total_orders,
            option.category.casefold(),
            option.meal_id,
        )
    )
    meal_slot = 0 if meal_key == 'lunch' else 1
    option = main_meals[(day_index * 2 + meal_slot) % len(main_meals)]
    return {
        'category': option.category,
        'meal_id': option.meal_id,
        'total_orders': option.total_orders,
    }


def _build_meal(catalog, meal, daily_calories, day_index, used_names, indian_options):
    inspiration = _indian_menu_inspiration(indian_options, day_index, meal['key'])
    selected = _choose_foods(catalog, meal, day_index, used_names, inspiration)
    if not selected:
        return None

    meal_target = Decimal(daily_calories) * meal['calorie_share']
    portions = []
    for index, (food, role) in enumerate(selected):
        role_share = meal['roles'][index][1] if index < len(meal['roles']) else Decimal(1) / len(selected)
        servings = _portion_for(meal_target * role_share, food.calories)
        portions.append({
            'food': food,
            'role': role,
            'servings': servings,
            'calories': Decimal(food.calories) * servings,
            'protein_g': Decimal(food.protein_g) * servings,
            'carbohydrates_g': Decimal(food.carbohydrates_g) * servings,
            'fat_g': Decimal(food.fat_g) * servings,
        })
        used_names.add(food.name)

    totals = {
        key: sum((item[key] for item in portions), Decimal('0'))
        for key in ('calories', 'protein_g', 'carbohydrates_g', 'fat_g')
    }
    return {
        **meal,
        'foods': portions,
        'menu_inspiration': inspiration,
        **{key: round(value) for key, value in totals.items()},
    }


def generate_weekly_plan(
    food_catalog,
    daily_calories,
    diet_type,
    allergies='',
    indian_options=(),
):
    catalog = _eligible_foods(food_catalog, diet_type, allergies)
    if not catalog:
        return []

    calorie_target = Decimal(daily_calories)
    week = []
    for day_index, day_name in enumerate(
        ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    ):
        used_names = set()
        meals = [
            generated
            for meal in MEALS
            if (
                generated := _build_meal(
                    catalog,
                    meal,
                    calorie_target,
                    day_index,
                    used_names,
                    indian_options,
                )
            )
        ]
        totals = {
            key: sum(meal[key] for meal in meals)
            for key in ('calories', 'protein_g', 'carbohydrates_g', 'fat_g')
        }
        week.append({'name': day_name, 'meals': meals, **totals})
    return week
