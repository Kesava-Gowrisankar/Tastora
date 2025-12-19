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

from django.views.generic import DetailView,ListView, FormView
from .forms import CollectionForm
from .domains import create_recipe_with_details, update_recipe_with_details
from .models import Recipe, Nutrition, Ingredient, RecipeImage, RecipeLike, Collection
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
        return redirect('recipe:recipe_detail', pk=recipe.pk)
    
    def forms_are_valid(self, forms):
        results = [form.is_valid() for form in forms.values() if hasattr(form, 'is_valid')]
        return all(results)
    
class ToggleLikeView(LoginRequiredMixin, View):
    """
    Toggle like/unlike for a recipe via AJAX.
    Returns JSON with updated like status and count.
    """

    def post(self, request, pk, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        like, created = RecipeLike.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            # Unlike if it already existed
            like.delete()
            liked = False
        else:
            # Liked
            liked = True

        total_likes = recipe.recipe_likes.count()
        
        return JsonResponse({
            'liked': liked,
            'total_likes': total_likes,
        })
    
class AddToCollectionView(LoginRequiredMixin, FormView):
    template_name = 'recipe/add_to_collection.html'
    form_class = CollectionForm

    def dispatch(self, request, *args, **kwargs):
        self.recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        self.collections = request.user.collections.all()
        self.recipe_collections = self.collections.filter(recipes=self.recipe).values_list('id', flat=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_collection = form.save(commit=False)
        new_collection.owner = self.request.user
        new_collection.save()
        new_collection.recipes.add(self.recipe)
        return redirect('recipe:add_to_collection', recipe_id=self.recipe.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'recipe': self.recipe,
            'collections': self.collections,
            'recipe_collections': list(self.recipe_collections),
        })
    
class AddToCollectionView(LoginRequiredMixin, FormView):
    template_name = 'recipe/add_to_collection.html'
    form_class = CollectionForm

    def dispatch(self, request, *args, **kwargs):
        self.recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        self.collections = request.user.collections.all()
        self.recipe_collections = self.collections.filter(recipes=self.recipe).values_list('id', flat=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_collection = form.save(commit=False)
        new_collection.owner = self.request.user
        new_collection.save()
        new_collection.recipes.add(self.recipe)
        return redirect('recipe:add_to_collection', recipe_id=self.recipe.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'recipe': self.recipe,
            'collections': self.collections,
            'recipe_collections': list(self.recipe_collections),
        })
    
class AddToCollectionView(LoginRequiredMixin, FormView):
    template_name = 'recipe/add_to_collection.html'
    form_class = CollectionForm

    def dispatch(self, request, *args, **kwargs):
        self.recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        self.collections = request.user.collections.all()
        self.recipe_collections = self.collections.filter(recipes=self.recipe).values_list('id', flat=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_collection = form.save(commit=False)
        new_collection.owner = self.request.user
        new_collection.save()
        new_collection.recipes.add(self.recipe)
        return redirect('recipe:add_to_collection', recipe_id=self.recipe.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'recipe': self.recipe,
            'collections': self.collections,
            'recipe_collections': list(self.recipe_collections),
        })
    
class AddToCollectionView(LoginRequiredMixin, FormView):
    template_name = 'recipe/add_to_collection.html'
    form_class = CollectionForm

    def dispatch(self, request, *args, **kwargs):
        self.recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        self.collections = request.user.collections.all()
        self.recipe_collections = self.collections.filter(recipes=self.recipe).values_list('id', flat=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        new_collection = form.save(commit=False)
        new_collection.owner = self.request.user
        new_collection.save()
        new_collection.recipes.add(self.recipe)
        return redirect('recipe:add_to_collection', recipe_id=self.recipe.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'recipe': self.recipe,
            'collections': self.collections,
            'recipe_collections': list(self.recipe_collections),
        })
        return context


# Class-based view to toggle a recipe in/out of a collection
class ToggleCollectionMembershipView(LoginRequiredMixin, View):

    def post(self, request, recipe_id, collection_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        collection = get_object_or_404(Collection, pk=collection_id, owner=request.user)

        if collection.recipes.filter(pk=recipe.pk).exists():
            collection.recipes.remove(recipe)
        else:
            collection.recipes.add(recipe)

        return redirect('recipe:add_to_collection', recipe_id=recipe.id)

class AllCollectionView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = "recipe/all_collections.html"
    context_object_name = "collections"

    def get_queryset(self):
        # Prefetch recipes for efficiency
        return Collection.objects.filter(owner=self.request.user).prefetch_related('recipes')


class CollectionDetailView(LoginRequiredMixin, View):
    template_name = "recipe/collection_detail.html"

    def get(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, owner=request.user)
        recipes = collection.recipes.prefetch_related('images')
        form = CollectionForm(instance=collection)
        return render(request, self.template_name, {
            'collection': collection,
            'recipes': recipes,
            'form': form,
        })

    def post(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, owner=request.user)

        if "update_name" in request.POST:
            form = CollectionForm(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect('recipe:collection_detail', pk=collection.pk)

        elif "delete_collection" in request.POST:
            collection.delete()
            return redirect('recipe:all_collections')

        elif "remove_recipe" in request.POST:
            recipe_id = request.POST.get("recipe_id")
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            collection.recipes.remove(recipe)
            return redirect('recipe:collection_detail', pk=collection.pk)

        # Only fetch recipes and form if rendering template due to error
        recipes = collection.recipes.prefetch_related('images')
        form = CollectionForm(instance=collection)
        return render(request, self.template_name, {
            'collection': collection,
            'recipes': recipes,
            'form': form,
        })

class DeleteCollectionView(LoginRequiredMixin, View):
    template_name = "recipe/confirm_delete_collection.html"

    def get(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, owner=request.user)
        return render(request, self.template_name, {'collection': collection})

    def post(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk, owner=request.user)
        collection.delete()
        return redirect('recipe:all_collections')
    
class AuthorRecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "recipe/author_recipes.html"
    context_object_name = "recipes"

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by('-created').prefetch_related('images')

class DeleteRecipeView(LoginRequiredMixin, View):
    template_name = "recipe/confirm_delete_recipe.html"

    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        return render(request, self.template_name, {'recipe': recipe})

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
        recipe.delete()
        return redirect('recipe:author_recipes')
