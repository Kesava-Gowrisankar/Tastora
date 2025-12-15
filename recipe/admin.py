from django.contrib import admin
from . import models

admin.site.register(models.Profile)
admin.site.register(models.Collection)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
admin.site.register(models.Nutrition)
admin.site.register(models.RecipeLike)
admin.site.register(models.RecipeImage)
