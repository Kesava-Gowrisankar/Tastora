from django.urls import path
from . import views

app_name = "recipe_management"
urlpatterns = [
    path("create/", views.CreateRecipeView.as_view(), name="create_recipe"),
    path("add-ingredient-form/", views.AddIngredientFormView.as_view(), name="add_ingredient_form"),
]
