# recipe/services.py
from django.db import transaction
from .models import Ingredient, Nutrition, Recipe, RecipeImage

def create_recipe_with_details(user, recipe_data, nutrition_data, image_data, ingredients_data):
    recipe = Recipe.objects.create(author=user, **recipe_data)
    Nutrition.objects.create(recipe=recipe, **nutrition_data)
    if image_data.get('image'):
        RecipeImage.objects.create(recipe=recipe, image=image_data['image'])
    for ing in ingredients_data:
        name = ing.get('name')
        Ingredient.objects.create(
            recipe=recipe,
            name=name,
            quantity=ing.get('quantity') or 0,
            unit=ing.get('unit'),
            optional=ing.get('optional', False),
        )


