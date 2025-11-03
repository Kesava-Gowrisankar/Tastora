from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.http import JsonResponse
from recipe.models import Recipe, Nutrition, Ingredient, RecipeImage, RecipeLike
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
                    return redirect('recipe_management:create_recipe')

            except Exception as e:
                messages.error(request, f"Error while saving the recipe: {e}")

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
        return render(request, 'recipe_management/forms/_ingredient_form.html', {'form': form, 'new_total': new_total})


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe_management/detail_recipe.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        user = self.request.user

        # Get first and second image safely
        first_img = recipe.get_first_image_url()
        nutrition = getattr(recipe, 'nutrition', None)
        ingredients = recipe.ingredients.all()
        liked = recipe.is_liked_by_user(user) if user.is_authenticated else False

        # Split instructions into lines (assuming instructions are stored as text with line breaks)
        points=recipe.instructions.split('.')
        instruction_list = [point.strip() for point in points if point.strip()]
        context.update({
            'first_img': first_img,
            'nutrition': nutrition,
            'ingredient': ingredients,
            'instruction': instruction_list,
            'liked': liked,
        })
        return context

@method_decorator(login_required, name='dispatch')
class EditRecipeView(View):
    template_name = 'recipe_management/edit_recipe.html'

    def get_forms(self, request, recipe):
        # Bind forms with instance
        recipe_form = RecipeForm(request.POST or None, request.FILES or None, instance=recipe, user=request.user)
        nutrition_form = NutritionForm(request.POST or None, instance=getattr(recipe, 'nutrition', None))
        recipe_image_form = RecipeImageForm(request.POST or None, request.FILES or None)
        # Ingredient formset pre-filled
        ingredient_formset = IngredientFormSetClass(
            request.POST or None,
            request.FILES or None,
            queryset=recipe.ingredients.all()
        )
        return {
            'recipeform': recipe_form,
            'nutritionform': nutrition_form,
            'recipe_image': recipe_image_form,
            'ingredient_formset': ingredient_formset,
            'recipe': recipe
        }

    def get(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        forms = self.get_forms(request, recipe)
        return render(request, self.template_name, forms)

    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        forms = self.get_forms(request, recipe)
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
                    # Update Recipe
                    recipe = recipe_form.save(commit=False)
                    recipe.author = request.user
                    recipe.save()

                    # Update Nutrition
                    nutrition = nutrition_form.save(commit=False)
                    nutrition.recipe = recipe
                    nutrition.save()

                    # Update Image
                    uploaded_image = recipe_image_form.cleaned_data.get('image')
                    recipe_default_image = 'default-recipe.jpg'

                    if uploaded_image and hasattr(uploaded_image, 'name') and uploaded_image.name != recipe_default_image:
                        image = recipe_image_form.save(commit=False)
                        image.recipe = recipe
                        image.save()

                    # Update Ingredients
                    # Delete removed ingredients
                    for form in ingredient_formset.deleted_forms:
                        if form.instance.pk:
                            form.instance.delete()
                    
                    # Save or update existing ingredients
                    for form in ingredient_formset:
                        if form.cleaned_data.get('DELETE'):
                            continue
                        name = form.cleaned_data.get('name')
                        if not name:
                            continue
                        ingredient = form.save(commit=False)
                        ingredient.recipe = recipe
                        ingredient.save()

                    messages.success(request, "Recipe updated successfully!")
                    return redirect('recipe_management:recipe_detail', pk=recipe.pk)

            except Exception as e:
                messages.error(request, f"Error while updating the recipe: {e}")
        else:
            # Provide detailed error messages to help the user see what failed
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

@login_required
def toggle_like(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    existing_like = RecipeLike.objects.filter(user=user, recipe=recipe)
    if existing_like.exists():
        # Unlike
        existing_like.delete()
        liked = False
    else:
        # Like
        RecipeLike.objects.create(user=user, recipe=recipe)
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': recipe.recipe_likes.count(),
    })
