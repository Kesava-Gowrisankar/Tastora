import re
from django.forms import formset_factory, modelform_factory, modelformset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator

from recipe.models import Recipe, Nutrition, Ingredient, RecipeImage
from .forms import IngredientFormSetClass, RecipeForm, NutritionForm, RecipeImageForm, IngredientForm

# Decorator to require login for CBV methods
def login_required_method(view):
    return method_decorator(login_required, name=view)

# Main CreateRecipeView as class-based view
@method_decorator(login_required, name='dispatch')
class CreateRecipeView(View):

    template_name = 'recipe_management/add_recipe.html'

    def get_forms(self, request):
        # Bind forms and formsets properly
        recipe_form = RecipeForm(request.POST or None, request.FILES or None, user=request.user)
        nutrition_form = NutritionForm(request.POST or None)
        recipe_image_form = RecipeImageForm(request.POST or None, request.FILES or None)
        ingredient_formset = IngredientFormSetClass(
            request.POST or None,
            request.FILES or None,
            queryset=Ingredient.objects.none()
        )
        return {
            'recipeform': recipe_form,
            'nutritionform': nutrition_form,
            'recipe_image': recipe_image_form,
            'ingredient_formset': ingredient_formset,
        }

    def get(self, request, *args, **kwargs):
        forms = self.get_forms(request)
        return render(request, self.template_name, forms)

    def post(self, request, *args, **kwargs):
        forms = self.get_forms(request)
        recipe_form = forms['recipeform']
        nutrition_form = forms['nutritionform']
        recipe_image_form = forms['recipe_image']
        ingredient_formset = forms['ingredient_formset']

        if (recipe_form.is_valid() and
            nutrition_form.is_valid() and
            recipe_image_form.is_valid() and
            ingredient_formset.is_valid()):

            try:
                with transaction.atomic():
                    # Save Recipe
                    recipe = recipe_form.save(commit=False)
                    recipe.author = request.user
                    recipe.save()

                    # Save Nutrition (OneToOne)
                    nutrition = nutrition_form.save(commit=False)
                    nutrition.recipe = recipe
                    nutrition.save()

                    # Save Image (ForeignKey)
                    if recipe_image_form.cleaned_data.get('image'):
                        image = recipe_image_form.save(commit=False)
                        image.recipe = recipe
                        image.save()

                    # Save Ingredients
                    for form in ingredient_formset:
                        if form.cleaned_data.get('DELETE'):
                            continue
                        name = form.cleaned_data.get('name')
                        if not name:
                            continue

                        ingredient = Ingredient(
                            recipe=recipe,
                            name=name,
                            quantity=form.cleaned_data.get('quantity') or 0,
                            unit=form.cleaned_data.get('unit'),
                            optional=form.cleaned_data.get('optional', False)
                        )
                        ingredient.save()

                    messages.success(request, "Recipe created successfully!")
                    return redirect('recipe:home')

            except Exception as e:
                messages.error(request, "An unexpected error occurred while saving the recipe.")

        else:
            # Collect detailed error messages
            err_msgs = []
            if not recipe_form.is_valid():
                err_msgs.append(f"Recipe errors: {recipe_form.errors}")
            if not nutrition_form.is_valid():
                err_msgs.append(f"Nutrition errors: {nutrition_form.errors}")
            if not recipe_image_form.is_valid():
                err_msgs.append(f"Image errors: {recipe_image_form.errors}")
            if not ingredient_formset.is_valid():
                err_msgs.append(f"Ingredient formset errors: {ingredient_formset.errors} {ingredient_formset.non_form_errors()}")

            messages.error(request, "Please correct the errors below. " + " | ".join(err_msgs))

        return render(request, self.template_name, forms)


# Separate class-based view for adding a new ingredient form via HTMX/ajax
@method_decorator(login_required, name='dispatch')
class AddIngredientFormView(View):
    def get(self, request, *args, **kwargs):
        formset = IngredientFormSetClass(queryset=Ingredient.objects.none())
        form = formset.empty_form

        index = request.GET.get('form-TOTAL_FORMS', '0')
        try:
            idx = int(index)
        except ValueError:
            idx = 0
        form.prefix = form.prefix.replace('__prefix__', str(idx))

        new_total = idx + 1
        return render(request, 'recipe_management/forms/_ingredient_form.html', {'form': form, 'new_total': new_total})
