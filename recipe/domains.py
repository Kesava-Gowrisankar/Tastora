# recipe/services.py
from django.db import transaction
from .models import Ingredient, Nutrition, Recipe, RecipeImage

@transaction.atomic
def create_recipe_with_details(user, recipe_data, nutrition_data, image_data, ingredients_data):
    recipe = Recipe.objects.create(author=user, **recipe_data)
    Nutrition.objects.create(recipe=recipe, **nutrition_data)
    
    image = image_data.get('image')
    if image and image != 'default-recipe.jpg':
        RecipeImage.objects.create(recipe=recipe, image=image)

    for ing in ingredients_data:
        Ingredient.objects.create(
            recipe=recipe,
            name=ing.get('name'),
            quantity=ing.get('quantity') or 0,
            unit=ing.get('unit'),
            optional=ing.get('optional', False),
        )

@transaction.atomic
def update_recipe_with_details(
    recipe,
    user,
    recipe_data,
    nutrition_data,
    image_data,
    ingredients_data,
):
    for field, value in recipe_data.items():
        setattr(recipe, field, value)
    recipe.author = user
    recipe.save()

    nutrition, _ = Nutrition.objects.get_or_create(recipe=recipe)
    for field, value in nutrition_data.items():
        setattr(nutrition, field, value)
    nutrition.save()

    uploaded_image = image_data.get('image')
    if uploaded_image and uploaded_image != 'default-recipe.jpg':
        RecipeImage.objects.create(recipe=recipe, image=uploaded_image)

    Ingredient.objects.filter(recipe=recipe).delete()
    Ingredient.objects.bulk_create([
        Ingredient(
            recipe=recipe,
            name=ingredient.get('name'),
            quantity=ingredient.get('quantity') or 0,
            unit=ingredient.get('unit'),
            optional=ingredient.get('optional', False),
        )
        for ingredient in ingredients_data
    ])
