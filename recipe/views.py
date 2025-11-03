from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import Recipe

class HomePage(ListView):
    model = Recipe
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.order_by('-created_at')[:5]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:5]
        return context


class RecipePage(ListView):
    model = Recipe
    template_name='recipe.html'

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe_detail.html'  
    context_object_name = 'recipe'  
