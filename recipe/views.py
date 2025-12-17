from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from recipe.models import Recipe, Nutrition, Ingredient, RecipeImage
from .forms import IngredientFormSetClass, RecipeForm, NutritionForm, RecipeImageForm, IngredientForm

RECIPES_ON_HOMEPAGE = 5

class HomePage(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.all()[:RECIPES_ON_HOMEPAGE]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:RECIPES_ON_HOMEPAGE]
        return context

# Main CreateRecipeView as class-based view
@method_decorator(login_required, name='dispatch')
class CreateRecipeView(View):

    template_name = 'recipe/add_recipe.html'

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
                    return redirect('recipe:create_recipe')

            except Exception:
                import logging
                logging.exception("An unexpected error occurred while saving the recipe")
                messages.error(request, "An unexpected error occurred while saving the recipe. Please try again.")

        else:
            messages.error(request, "Please correct the errors below.")

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
        return render(request, 'recipe/forms/_ingredient_form.html', {'form': form, 'new_total': new_total})

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe/detail_recipe.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()

        # Get first and second image safely
        first_img = recipe.get_first_image_url()
        nutrition = getattr(recipe, 'nutrition', None)
        ingredients = recipe.ingredients.all()

        # Split instructions into lines (assuming instructions are stored as text with line breaks)
        points=recipe.instructions.splitlines()
        instruction_list = [point.strip() for point in points if point.strip()]
        context.update({
            'first_img': first_img,
            'nutrition': nutrition,
            'ingredient': ingredients,
            'instruction': instruction_list,
        })
        return context