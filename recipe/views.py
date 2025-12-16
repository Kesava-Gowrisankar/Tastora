from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Recipe

RECIPES_ON_HOMEPAGE = 5
class HomePage(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.all()[:RECIPES_ON_HOMEPAGE]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:RECIPES_ON_HOMEPAGE]
        return context
