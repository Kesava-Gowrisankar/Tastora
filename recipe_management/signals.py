from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from recipe.models import RecipeLike


@receiver(post_save, sender=RecipeLike)
def update_likes_on_create(sender, instance, created, **kwargs):
    """Increase recipe like count when a user likes."""
    if created:
        recipe = instance.recipe
        recipe.likes = recipe.recipe_likes.count()
        recipe.save(update_fields=['likes'])


@receiver(post_delete, sender=RecipeLike)
def update_likes_on_delete(sender, instance, **kwargs):
    """Decrease recipe like count when a user unlikes."""
    recipe = instance.recipe
    recipe.likes = recipe.recipe_likes.count()
    recipe.save(update_fields=['likes'])
