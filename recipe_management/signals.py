from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from recipe.models import RecipeLike


@receiver(post_save, sender=RecipeLike)
def update_likes_on_create(sender, instance, created, **kwargs):
    """Increase recipe like count when a user likes."""
    if created:
        from recipe.models import Recipe
        from django.db.models import F
        Recipe.objects.filter(pk=instance.recipe.pk).update(likes=F('likes') + 1)
@receiver(post_delete, sender=RecipeLike)
def update_likes_on_delete(sender, instance, **kwargs):
    """Decrease recipe like count when a user unlikes."""
    from recipe.models import Recipe
    from django.db.models import F, Case, When
    Recipe.objects.filter(pk=instance.recipe.pk).update(
        likes=Case(
            When(likes__gt=0, then=F('likes') - 1),
            default=0
        )
    )
