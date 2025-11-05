from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import Recipe

class HomePage(ListView):
    model = Recipe
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Eagerly load related images to prevent N+1 queries in the template.
        recipes_qs = Recipe.objects.prefetch_related('images')
        context['latest_recipes'] = recipes_qs.order_by('-created_at')[:5]
        context['popular_recipes'] = recipes_qs.order_by('-likes')[:5]
        return context
