from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator
from .domains import create_recipe_with_details

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
    

@method_decorator(login_required, name='dispatch')
class CreateRecipeView(View):
    template_name = 'recipe/add_recipe.html'

    def forms_are_valid(self, forms):
        """Check that all forms are valid."""
        return all(form.is_valid() for form in forms.values())

    def get(self, request, *args, **kwargs):
        """Render the empty forms."""
        return render(request, self.template_name, self.get_forms(request))

    def post(self, request, *args, **kwargs):
        """Process submitted forms.""" 
        forms = self.get_forms(request)

        if not self.forms_are_valid(forms):
            messages.error(request, "Please correct the errors below.")
            return render(request, self.template_name, forms)

        recipe_data = forms['recipeform'].cleaned_data
        nutrition_data = forms['nutritionform'].cleaned_data
        image_data = forms['recipe_image'].cleaned_data
        ingredients_data = [f.cleaned_data for f in forms['ingredient_formset'] if f.cleaned_data]

        create_recipe_with_details(
            user=request.user,
            recipe_data=recipe_data,
            nutrition_data=nutrition_data,
            image_data=image_data,
            ingredients_data=ingredients_data
        )

        messages.success(request, "Recipe created successfully!")
        return redirect('recipe:create_recipe')
        
    def get_forms(self, request):
        """Return all forms and formsets."""
        return {
            'recipeform': RecipeForm(request.POST or None, request.FILES or None, user=request.user),
            'nutritionform': NutritionForm(request.POST or None),
            'recipe_image': RecipeImageForm(request.POST or None, request.FILES or None),
            'ingredient_formset': IngredientFormSetClass(
                request.POST or None,
                request.FILES or None,
                queryset=Ingredient.objects.none()
            ),
        }

    def forms_are_valid(self, forms):
        """Check that all forms are valid."""
        return all(form.is_valid() for form in forms.values())


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