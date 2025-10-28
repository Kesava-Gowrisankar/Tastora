from django.urls import path
from .views import CreateRecipeView, AddIngredientFormView

app_name = "recipe_management"  # ✅ Required for namespacing

urlpatterns = [
    path("manage/create/", CreateRecipeView.as_view(), name="create_recipe"),
    path("manage/add-ingredient-form/", AddIngredientFormView.as_view(), name="add_ingredient_form"),
]
