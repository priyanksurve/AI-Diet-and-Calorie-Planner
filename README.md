# AI Diet and Calorie Planner

A Django application that estimates daily calorie and macronutrient targets and creates a seven-day meal plan based on a member's profile, diet preference, and foods to avoid.

## Features

- Member registration, login, and protected planner pages.
- Calorie and macro estimates using the Mifflin–St Jeor equation.
- Seven-day meal suggestions built from imported nutrition records.
- Diet preference and name-based allergy/avoidance filtering.
- Indian meal-category inspiration using historical order counts.

## Requirements

- Python 3.10+
- MySQL
- The Food Nutrition Dataset and Indian Food Plan Dataset files, obtained from their original sources and stored locally as described below.

## Setup on Windows

From the project directory, create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local environment file and set its values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set a private `DJANGO_SECRET_KEY` and your local MySQL credentials. Do not commit `.env`.

Create the MySQL database named in `DB_NAME`, then run migrations:

```powershell
python manage.py migrate
```

## Datasets

Dataset files are not included in this repository. Obtain them from their original sources and make sure their terms allow your intended use.

Place the nutrition CSV files here:

```text
Food Nutrition Dataset/
└── FINAL FOOD DATASET/
    ├── FOOD-DATA-GROUP1.csv
    ├── FOOD-DATA-GROUP2.csv
    ├── FOOD-DATA-GROUP3.csv
    ├── FOOD-DATA-GROUP4.csv
    └── FOOD-DATA-GROUP5.csv
```

Place the Indian meal-demand CSV files here:

```text
Indian Food Plan Dataset/
└── foodDemand_train/
    ├── meal_info.csv
    └── train.csv
```

Import the records:

```powershell
python manage.py import_food_dataset
python manage.py import_indian_meal_dataset
```

The Food Nutrition Dataset supplies the food names and calorie/macronutrient values used by the meal planner. The Indian Food Plan Dataset provides cuisine/category labels and historical demand counts; it does not contain recipes or nutrient values. Nutrition in generated plans therefore comes from the food nutrition catalog.

## Run

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, create an account, then use the calculator and weekly plan.

## Deploy to Vercel

Set the Vercel project root directory to `AI_Diet_Planner` if deploying from the parent repository. Add these environment variables in the Vercel project settings:

- `DJANGO_SECRET_KEY`: a long, private random value.
- `DJANGO_DEBUG`: `False`.
- `DJANGO_ALLOWED_HOSTS`: your Vercel domain (for example, `your-project.vercel.app`).
- `DB_ENGINE`: `django.db.backends.mysql`.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`: credentials for a MySQL database reachable from Vercel.

Vercel detects the Django application from `manage.py` and its WSGI settings, and collects the configured static files during deployment. The application uses PyMySQL so deployment does not need native MySQL build tools. Vercel's temporary filesystem is not a persistent database, so configure an external MySQL service rather than SQLite or a local database file.

## Notes

- Nutrition entries do not define consistent serving weights. Displayed portions are multiples of a dataset entry, not grams or household measures.
- Food-name matching cannot verify hidden ingredients or cross-contamination. Check labels, especially when managing allergies.
- Estimates and generated meal ideas are informational and are not medical advice.
- Keep local databases, dataset files, environment files, and virtual environments out of public commits.
