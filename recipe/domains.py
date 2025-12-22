# recipe/services.py
from django.db import transaction
from .models import Ingredient, Nutrition, Recipe, RecipeImage

@transaction.atomic
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

@transaction.atomic
def update_recipe_with_details(
    recipe,
    user,
    recipe_data,
    nutrition_data,
    image_data,
    ingredients_data,
):
    # --- Update Recipe ---
    for field, value in recipe_data.items():
        setattr(recipe, field, value)
    recipe.author = user
    recipe.save()

    # --- Nutrition ---
    nutrition, _ = Nutrition.objects.get_or_create(recipe=recipe)
    for field, value in nutrition_data.items():
        setattr(nutrition, field, value)
    nutrition.save()

    # --- Image ---
    uploaded_image = image_data.get('image')
    if uploaded_image:
        RecipeImage.objects.create(recipe=recipe, image=uploaded_image)

    # --- Ingredients (rebuild from scratch) ---
    Ingredient.objects.filter(recipe=recipe).delete()

    Ingredient.objects.bulk_create([
        Ingredient(
            recipe=recipe,
            name=ing.get('name'),
            quantity=ing.get('quantity') or 0,
            unit=ing.get('unit'),
            optional=ing.get('optional', False),
        )
        for ing in ingredients_data
    ])
