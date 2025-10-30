from operator import add
from django.urls import path
from . import views

app_name = "recipe_management"
urlpatterns = [
    path("manage/create/", views.CreateRecipeView.as_view(), name="create_recipe"),
    path("manage/add-ingredient-form/", views.AddIngredientFormView.as_view(), name="add_ingredient_form"),
]
