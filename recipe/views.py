from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Recipe
from django.core.paginator import Paginator
from django.db.models import Q

RECIPES_ON_HOMEPAGE = 5
class HomePage(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_recipes'] = Recipe.objects.order_by('-created')[:RECIPES_ON_HOMEPAGE]
        context['popular_recipes'] = Recipe.objects.order_by('-likes')[:RECIPES_ON_HOMEPAGE]
        return context  

def recipe_list(request):
    recipes = Recipe.objects.all()

    # --- Filters ---
    category = request.GET.get("category")
    difficulty = request.GET.get("difficulty")
    cuisine = request.GET.get("cuisine")
    search = request.GET.get("search")

    if category and category != "all":
        recipes = recipes.filter(category=category)

    if difficulty and difficulty != "all":
        recipes = recipes.filter(difficulty=difficulty)

    if cuisine and cuisine.strip():
        recipes = recipes.filter(cuisine__icontains=cuisine)

    if search:
        recipes = recipes.filter(
            Q(title__icontains=search) |
            Q(cuisine__icontains=search)
        )

    # Pagination — 20 per page
    paginator = Paginator(recipes.order_by('-created'), 1)
    page = request.GET.get('page')
    recipes_page = paginator.get_page(page)

    context = {
        "recipes": recipes_page,
        "paginator": paginator,
    }

    return render(request, "recipe.html", context)
