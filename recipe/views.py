from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Recipe

class HomePage(TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.order_by('-created')[:5]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:5]
        return context
