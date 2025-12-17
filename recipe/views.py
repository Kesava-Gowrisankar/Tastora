from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator
from .domains import create_recipe_with_details
from django.utils import timezone

from django.views.generic import DetailView
from .domains import create_recipe_with_details, update_recipe_with_details
from recipe.models import Recipe, Nutrition, Ingredient, RecipeImage
from .forms import IngredientFormSetClass, RecipeForm, NutritionForm, RecipeImageForm, IngredientForm
from .forms import IngredientFormSetClass, RecipeForm, NutritionForm, RecipeImageForm, IngredientForm
from django.contrib.auth.mixins import LoginRequiredMixin

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

        instruction_list = [point.strip() for point in recipe.instructions.split(".") if point.strip() ]

        liked = False
        if self.request.user.is_authenticated:
            liked = recipe.liked_by.filter(
                id=self.request.user.id
            ).exists()

        context.update({
            'instructions': instruction_list,
            'liked': liked,
            'now': timezone.now()
        })

        return context

@method_decorator(login_required, name='dispatch')
class EditRecipeView(View):
    template_name = 'recipe/edit_recipe.html'

    def get_forms(self, request, recipe):
        return {
            'recipeform': RecipeForm(
                request.POST or None,
                request.FILES or None,
                instance=recipe,
                user=request.user
            ),
            'nutritionform': NutritionForm(
                request.POST or None,
                instance=getattr(recipe, 'nutrition', None)
            ),
            'recipe_image': RecipeImageForm(
                request.POST or None,
                request.FILES or None
            ),
            'ingredient_formset': IngredientFormSetClass(
                request.POST or None,
                queryset=recipe.ingredients.all()
            ),
            'recipe': recipe,
        }

    def get(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        return render(request, self.template_name, self.get_forms(request, recipe))

    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        forms = self.get_forms(request, recipe)

        if not self.forms_are_valid(forms):
            messages.error(request, "Please correct the errors below.")
            return render(request, self.template_name, forms)

        update_recipe_with_details(
            recipe=recipe,
            user=request.user,
            recipe_data=forms['recipeform'].cleaned_data,
            nutrition_data=forms['nutritionform'].cleaned_data,
            image_data=forms['recipe_image'].cleaned_data,
            ingredients_data=[
                f.cleaned_data
                for f in forms['ingredient_formset']
                if f.cleaned_data and not f.cleaned_data.get('DELETE')
            ],
        )

        messages.success(request, "Recipe updated successfully!")
        return redirect('recipe:edit_recipe', pk=recipe.pk)
    
    def forms_are_valid(self, forms):
        results = [form.is_valid() for form in forms.values() if hasattr(form, 'is_valid')]
        return all(results)
    
