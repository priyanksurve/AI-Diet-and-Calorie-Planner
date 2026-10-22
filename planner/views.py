
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .calculations import calculate_targets
from .forms import CalculatorForm, RegistrationForm
from .meal_planner import generate_weekly_plan
from .models import Food, IndianMealOption


def home(request):
    return render(request, 'planner/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('calculator')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('calculator')

    return render(request, 'planner/register.html', {'form': form})


@login_required
def calculator(request):
    form = CalculatorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        request.session['diet_planner_input'] = form.cleaned_data
        return redirect('plan')

    return render(request, 'planner/calculator.html', {'form': form})


@login_required
def plan(request):
    calculator_data = request.session.get('diet_planner_input')
    if not calculator_data:
        return redirect(reverse('calculator'))

    form = CalculatorForm(data=calculator_data)
    if not form.is_valid():
        request.session.pop('diet_planner_input', None)
        return redirect(reverse('calculator'))

    calculator_data = form.cleaned_data
    calculation_inputs = {
        key: calculator_data[key]
        for key in ('age', 'gender', 'height_cm', 'weight_kg', 'activity_level', 'goal')
    }
    targets = calculate_targets(**calculation_inputs)
    weekly_plan = generate_weekly_plan(
        Food.objects.all(),
        targets.daily_calories,
        calculator_data['diet_type'],
        calculator_data['allergies'],
        IndianMealOption.objects.filter(cuisine__iexact='Indian'),
    )
    plan_message = None
    if not weekly_plan:
        plan_message = (
            'The food catalog is empty or has no suitable matches. '
            'Run "python manage.py migrate", "python manage.py import_food_dataset", '
            'and "python manage.py import_indian_meal_dataset", then try again.'
        )

    return render(
        request,
        'planner/plan.html',
        {
            'targets': targets,
            'weekly_plan': weekly_plan,
            'plan_message': plan_message,
        },
    )