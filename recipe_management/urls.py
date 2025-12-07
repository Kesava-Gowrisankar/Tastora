from django.urls import path
from . import views

app_name = "recipe_management"

urlpatterns = [
    # Recipe Management
    path("manage/create/", views.CreateRecipeView.as_view(), name="create_recipe"),
    path("manage/add-ingredient-form/", views.AddIngredientFormView.as_view(), name="add_ingredient_form"),
    path("recipe/<int:pk>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("recipe/<int:pk>/edit/", views.EditRecipeView.as_view(), name="edit_recipe"),
    path("recipe/<int:pk>/like/", views.ToggleLikeView.as_view(), name="toggle_like"),

    # Collections (Add, Toggle)
    path("recipe/<int:recipe_id>/add-to-collection/", views.AddToCollectionView.as_view(), name="add_to_collection"),
    path("recipe/<int:recipe_id>/toggle-collection/<int:collection_id>/", views.ToggleCollectionMembershipView.as_view(), name="toggle_collection_membership"),

    #Collections (List, Detail/Edit/Delete)
    path("collections/", views.AllCollectionView.as_view(), name="all_collections"),
    path("collections/<int:pk>/", views.CollectionDetailView.as_view(), name="collection_detail"),
    path("collections/<int:pk>/delete/", views.DeleteCollectionView.as_view(), name="delete_collection"),

    # Author Recipes
    path("author/recipes/", views.AuthorRecipeListView.as_view(), name="author_recipes"),
    path("recipe/<int:pk>/delete/", views.DeleteRecipeView.as_view(), name="delete_recipe"),
]
