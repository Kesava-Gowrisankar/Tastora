from django.contrib import admin
from .models import Collection, Ingredient, Nutrition, Recipe, RecipeImage, Profile

# -----------------------------
# Recipe Admin
# -----------------------------
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'difficulty', 'featured', 'likes', 'created_at')
    search_fields = ('title', 'cuisine', 'author__username', 'instructions')
    list_filter = ('category', 'difficulty', 'featured', 'cuisine')
    ordering = ('-created_at',)
    readonly_fields = ('likes',)

# -----------------------------
# Ingredient Admin
# -----------------------------
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipe', 'quantity', 'unit', 'optional')
    search_fields = ('name', 'recipe__title')
    list_filter = ('unit', 'optional')
    ordering = ('recipe', 'name')

# -----------------------------
# Nutrition Admin
# -----------------------------
class NutritionAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'calories', 'protein', 'fat', 'sugar', 'fiber', 'carbohydrates')
    search_fields = ('recipe__title',)
    ordering = ('recipe',)

# -----------------------------
# RecipeImage Admin
# -----------------------------
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image', 'created_at')
    search_fields = ('recipe__title',)
    ordering = ('-created_at',)

# -----------------------------
# Collection Admin
# -----------------------------
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__username')
    ordering = ('-created_at',)
    filter_horizontal = ('recipes',)  # easier to manage many-to-many recipes

# -----------------------------
# Profile Admin
# -----------------------------
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'bio', 'location')
    ordering = ('-created_at',)

# -----------------------------
# Register all models
# -----------------------------
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Nutrition, NutritionAdmin)
admin.site.register(RecipeImage, RecipeImageAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Profile, ProfileAdmin)
