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

    
    submitted_ids = set()

    ingredients_to_create = []
    ingredients_to_update = []

    # Separate ingredients into create and update lists
    for ing_data in ingredients_data:
        ingredient_instance = ing_data.get('id')

        if ingredient_instance:
            ingredient = ingredient_instance
            ingredient.name = ing_data.get('name')
            ingredient.quantity = ing_data.get('quantity') or 0
            ingredient.unit = ing_data.get('unit')
            ingredient.optional = ing_data.get('optional', False)
            ingredients_to_update.append(ingredient)
            submitted_ids.add(ingredient.id)
        else:
            ingredients_to_create.append(
                Ingredient(
                    recipe=recipe,
                    name=ing_data.get('name'),
                    quantity=ing_data.get('quantity') or 0,
                    unit=ing_data.get('unit'),
                    optional=ing_data.get('optional', False),
                )
            )

    # Perform bulk operations
    if ingredients_to_update:
        Ingredient.objects.bulk_update(ingredients_to_update, ['name', 'quantity', 'unit', 'optional'])

    if ingredients_to_create:
        created_ingredients = Ingredient.objects.bulk_create(ingredients_to_create)
        for ing in created_ingredients:
            submitted_ids.add(ing.id)

    # --- Delete removed ingredients ---
    Ingredient.objects.filter(
        recipe=recipe
    ).exclude(id__in=submitted_ids).delete()
