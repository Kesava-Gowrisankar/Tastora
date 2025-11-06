from django.urls import path
from . import views

app_name = "recipe_management"
urlpatterns = [
    path("manage/create/", views.CreateRecipeView.as_view(), name="create_recipe"),
    path("manage/add-ingredient-form/", views.AddIngredientFormView.as_view(), name="add_ingredient_form"),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.EditRecipeView.as_view(), name='edit_recipe'),
]
