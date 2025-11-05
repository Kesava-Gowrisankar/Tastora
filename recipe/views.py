# recipe/views.py
from ast import List
from string import Template
from django.views.generic import ListView, DetailView, TemplateView
from .models import Recipe
from django.db.models import Q

class HomePage(ListView):
    model = Recipe
    template_name = 'home.html'
    context_object_name = 'recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.order_by('-created_at')[:5]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:5]
        return context


class RecipePage(ListView):
    model = Recipe
    template_name = 'recipe.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        queryset = Recipe.objects.all()

        # Get search term and filters
        query = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        difficulty = self.request.GET.get('difficulty', '').strip()
        cuisine = self.request.GET.get('cuisine', '').strip()
        min_likes = self.request.GET.get('min_likes', '').strip()
        sort_by = self.request.GET.get('sort_by', '').strip()

        # 🔍 Search across title, cuisine, and author name (optional)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(cuisine__icontains=query)
            )

        # 🧩 Apply other filters
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if cuisine:
            queryset = queryset.filter(cuisine__icontains=cuisine)
        if min_likes.isdigit():
            queryset = queryset.filter(likes__gte=int(min_likes))

        # 🧭 Sorting
        if sort_by == 'popular':
            queryset = queryset.order_by('-likes', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Recipe.CategoryTypes.CHOICES
        context['difficulties'] = Recipe.DifficultyLevels.CHOICES
        context['current_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort_by', '')
        return context


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipe_detail.html'
    context_object_name = 'recipe'

class Aboutpage(ListView):
    template_name = 'about.html'
    model = Recipe
