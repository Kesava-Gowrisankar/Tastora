from django.urls import path
from . import views
app_name='recipe'
urlpatterns=[
    path('home/',views.HomePage.as_view(),name='home'),
    path('recipes/',views.RecipePage.as_view(),name='recipes'),
    path('recipe/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
]
