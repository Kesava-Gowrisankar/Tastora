from django.contrib import admin
from . import models

admin.site.register(models.Collection)
admin.site.register(models.Nutrition)
admin.site.register(models.Recipe)
admin.site.register(models.RecipeImage)
admin.site.register(models.Profile)


