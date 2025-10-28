from decimal import Decimal, InvalidOperation
from itertools import zip_longest

from django.db import IntegrityError, transaction
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from recipe.models import Recipe, Nutrition, Ingredient, RecipeImage
from .forms import RecipeForm, NutritionForm, RecipeImageForm


class CreateRecipeView(View):
    template_name = 'recipe_management/add_recipe.html'

    def get(self, request, *args, **kwargs):
        recipe_form = RecipeForm(user=request.user)
        nutrition_form = NutritionForm()
        image_form = RecipeImageForm()
        return render(request, self.template_name, {
            'recipeform': recipe_form,
            'nutritionform': nutrition_form,
            'recipe_image': image_form,
        })

    def post(self, request, *args, **kwargs):
        recipe_form = RecipeForm(request.POST, request.FILES, user=request.user)
        nutrition_form = NutritionForm(request.POST)
        image_form = RecipeImageForm(request.POST, request.FILES)
        ingredient_names = request.POST.getlist('ingredient_name[]')

        if not any(name.strip() for name in ingredient_names):
            messages.error(request, "⚠️ Please add at least one ingredient for the recipe.")
            return render(request, self.template_name, {
                'recipeform': recipe_form,
                'nutritionform': nutrition_form,
                'recipe_image': image_form,
            })

        try:
            with transaction.atomic():
                # Validate forms first
                if recipe_form.is_valid() and nutrition_form.is_valid() and image_form.is_valid():
                    # Save Recipe
                    recipe = recipe_form.save(commit=False)
                    recipe.author = request.user
                    recipe.save()

                    # Save Nutrition
                    nutrition = nutrition_form.save(commit=False)
                    nutrition.recipe = recipe
                    nutrition.save()

                    # Save Recipe Image
                    recipe_image = image_form.save(commit=False)
                    recipe_image.recipe = recipe
                    recipe_image.save()

                    # Save Ingredients
                    ingredient_quantities = request.POST.getlist('ingredient_quantity[]')
                    ingredient_units = request.POST.getlist('ingredient_unit[]')
                    ingredient_optionals = request.POST.getlist('ingredient_optional[]')

                    for name, quantity, unit, optional in zip_longest(
                        ingredient_names, ingredient_quantities, ingredient_units, ingredient_optionals, fillvalue=''
                    ):
                        clean_name = (name or '').strip()
                        if not clean_name:
                            continue
                        try:
                            Ingredient.objects.create(
                                recipe=recipe,
                                name=clean_name.lower(),
                                quantity=Decimal(quantity or "0"),
                                unit=int(unit or 0),
                                optional=(optional == "True")
                            )
                        except (ValueError, InvalidOperation):
                            messages.warning(request, f"⚠️ Invalid data for ingredient '{clean_name}'. It was skipped.")
                            continue

                    messages.success(request, "🎉 Recipe created successfully!")
                    return redirect('recipe_management:create_recipe')
                else:
                    # Collect all form errors
                    for form in [recipe_form, nutrition_form, image_form]:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"⚠️ {error}")

        except IntegrityError:
            messages.error(request, "⚠️ A database error occurred. Please check your inputs and try again.")

        return render(request, self.template_name, {
            'recipeform': recipe_form,
            'nutritionform': nutrition_form,
            'recipe_image': image_form,
        })


class AddIngredientFormView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "recipe_management/forms/_ingredient_form.html")
