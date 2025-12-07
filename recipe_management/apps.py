from django.apps import AppConfig


class RecipeManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipe_management'

    def ready(self):
        import recipe_management.signals
