from dataclasses import dataclass


ACTIVITY_FACTORS = {
    'low': 1.2,
    'moderate': 1.55,
    'high': 1.725,
}


@dataclass(frozen=True)
class DietTargets:
    bmr: int
    maintenance_calories: int
    daily_calories: int
    protein_g: int
    carbohydrates_g: int
    fat_g: int


def calculate_targets(
    age: int,
    gender: str,
    height_cm: float,
    weight_kg: float,
    activity_level: str,
    goal: str,
) -> DietTargets:
    if gender not in {'male', 'female'}:
        raise ValueError('Gender must be "male" or "female".')
    if activity_level not in ACTIVITY_FACTORS:
        raise ValueError('Activity level must be "low", "moderate", or "high".')
    if goal not in {'lose', 'maintain', 'gain'}:
        raise ValueError('Goal must be "lose", "maintain", or "gain".')

    gender_adjustment = 5 if gender == 'male' else -161
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + gender_adjustment
    maintenance_calories = bmr * ACTIVITY_FACTORS[activity_level]

    if goal == 'lose':
        calorie_adjustment = min(500, maintenance_calories * 0.2)
    elif goal == 'gain':
        calorie_adjustment = min(300, maintenance_calories * 0.1)
    else:
        calorie_adjustment = 0

    daily_calories = maintenance_calories
    if goal == 'lose':
        daily_calories -= calorie_adjustment
    elif goal == 'gain':
        daily_calories += calorie_adjustment

    protein_g = round(weight_kg * 1.6)
    fat_g = round(weight_kg * 0.8)
    carbohydrates_g = max(0, round((daily_calories - protein_g * 4 - fat_g * 9) / 4))

    return DietTargets(
        bmr=round(bmr),
        maintenance_calories=round(maintenance_calories),
        daily_calories=round(daily_calories),
        protein_g=protein_g,
        carbohydrates_g=carbohydrates_g,
        fat_g=fat_g,
    )
