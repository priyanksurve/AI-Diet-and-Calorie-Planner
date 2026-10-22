from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'new-password',
        })


class CalculatorForm(forms.Form):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    age = forms.IntegerField(
        min_value=18,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'max': 120}),
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        label='Sex used for this estimate',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    height_cm = forms.FloatField(
        min_value=100,
        max_value=250,
        label='Height (cm)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 100, 'max': 250, 'step': '0.1'}),
    )
    weight_kg = forms.FloatField(
        min_value=30,
        max_value=300,
        label='Weight (kg)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 30, 'max': 300, 'step': '0.1'}),
    )
    activity_level = forms.ChoiceField(
        choices=UserProfile.ACTIVITY_CHOICES,
        label='Activity level',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    goal = forms.ChoiceField(
        choices=UserProfile.GOAL_CHOICES,
        label='Your goal',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    diet_type = forms.ChoiceField(
        choices=[
            ('veg', 'Vegetarian'),
            ('vegan', 'Vegan'),
            ('nonveg', 'Non-vegetarian'),
        ],
        label='Diet preference',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    allergies = forms.CharField(
        required=False,
        label='Allergies or foods to avoid',
        help_text='Optional; separate multiple items with commas.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. peanuts, dairy',
        }),
    )
