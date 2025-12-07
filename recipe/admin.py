from django.contrib import admin
from django.utils.html import format_html
from .models import Collection, Ingredient, Nutrition, Recipe, RecipeImage, Profile, RecipeLike


# -----------------------------
# Recipe Admin
# -----------------------------
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'difficulty',
        'featured', 'likes', 'created', 'thumbnail_preview'
    )
    search_fields = ('title', 'cuisine', 'author__username', 'instructions')
    list_filter = ('category', 'difficulty', 'featured', 'cuisine')
    ordering = ('-created',)
    readonly_fields = ('likes',)
    autocomplete_fields = ('author',)
    list_select_related = ('author',)

    def get_queryset(self, request):
        """
        Optimize admin list query to prefetch related images,
        avoiding N+1 queries when calling thumbnail_preview().
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('images')  # <-- assumes related_name='images' in RecipeImage

    def thumbnail_preview(self, obj):
        """Show small recipe image preview if available."""
        # Now this doesn't hit DB each time because of prefetch_related
        image = next(iter(obj.images.all()), None)
        if image and image.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:5px; object-fit:cover;" />',
                image.image.url
            )
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
    list_display = ('recipe', 'image_preview', 'created')
    search_fields = ('recipe__title',)
    ordering = ('-created',)
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
    list_display = ('title', 'owner', 'created')
    search_fields = ('title', 'owner__username')
    ordering = ('-created',)
    filter_horizontal = ('recipes',)
    autocomplete_fields = ('owner',)
    list_select_related = ('owner',)


# -----------------------------
# Profile Admin
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created')
    search_fields = ('user__username', 'bio', 'location')
    ordering = ('-created',)
    list_select_related = ('user',)
    list_filter = ('location',)

@admin.register(RecipeLike)
class RecipeLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created', 'recipe_thumbnail')
    search_fields = ('user__username', 'recipe__title')
    list_filter = ('created', 'recipe__category', 'recipe__difficulty')
    ordering = ('-created',)
    autocomplete_fields = ('user', 'recipe')
    list_select_related = ('user', 'recipe')

    def recipe_thumbnail(self, obj):
        """Display a small thumbnail of the liked recipe"""
        image = obj.recipe.images.first()
        if image and image.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:5px; object-fit:cover;" />',
                image.image.url
            )
        return "—"
    recipe_thumbnail.short_description = "Recipe"