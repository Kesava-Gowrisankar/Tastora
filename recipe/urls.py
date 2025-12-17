from django.urls import path
from . import views
app_name='recipe'
urlpatterns=[
    path('',views.HomePage.as_view(),name='home'),
    path("create/", views.CreateRecipeView.as_view(), name="create_recipe"),
    path("add-ingredient-form/", views.AddIngredientFormView.as_view(), name="add_ingredient_form"),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.EditRecipeView.as_view(), name='edit_recipe'),
    path('recipe/<int:pk>/toggle-like/', views.ToggleLikeView.as_view(), name='toggle_like'),
]
