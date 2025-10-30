from django.contrib import admin
from django.utils.html import format_html
from .models import Collection, Ingredient, Nutrition, Recipe, RecipeImage, Profile


# -----------------------------
# Recipe Admin
# -----------------------------
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'difficulty',
        'featured', 'likes', 'created_at', 'thumbnail_preview'
    )
    search_fields = ('title', 'cuisine', 'author__username', 'instructions')
    list_filter = ('category', 'difficulty', 'featured', 'cuisine')
    ordering = ('-created_at',)
    readonly_fields = ('likes',)
    autocomplete_fields = ('author',)
    list_select_related = ('author',)

    def thumbnail_preview(self, obj):
        """Show small recipe image preview if available"""
        image = RecipeImage.objects.filter(recipe=obj).first()
        if image and image.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:5px; object-fit:cover;" />', image.image.url)
        return "—"
    thumbnail_preview.short_description = "Preview"


# -----------------------------
# Ingredient Admin
# -----------------------------
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'recipe', 'quantity', 'unit', 'optional')
    search_fields = ('name', 'recipe__title')
    list_filter = ('unit', 'optional')
    ordering = ('recipe', 'name')
    autocomplete_fields = ('recipe',)
    list_select_related = ('recipe',)


# -----------------------------
# Nutrition Admin
# -----------------------------
@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'calories', 'protein', 'fat', 'sugar', 'fiber', 'carbohydrates')
    search_fields = ('recipe__title',)
    ordering = ('recipe',)
    autocomplete_fields = ('recipe',)
    list_select_related = ('recipe',)


# -----------------------------
# RecipeImage Admin
# -----------------------------
@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image_preview', 'created_at')
    search_fields = ('recipe__title',)
    ordering = ('-created_at',)
    autocomplete_fields = ('recipe',)
    list_select_related = ('recipe',)

    def image_preview(self, obj):
        """Show small image preview in admin list"""
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:5px; object-fit:cover;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Image"


# -----------------------------
# Collection Admin
# -----------------------------
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    search_fields = ('title', 'owner__username')
    ordering = ('-created_at',)
    filter_horizontal = ('recipes',)
    autocomplete_fields = ('owner',)
    list_select_related = ('owner',)


# -----------------------------
# Profile Admin
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'bio', 'location')
    ordering = ('-created_at',)
    list_select_related = ('user',)
    list_filter = ('location',)
