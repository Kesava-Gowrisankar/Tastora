from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.db import models
from recipe.models import RecipeLike, Recipe

# Before creating a like
@receiver(pre_save, sender=RecipeLike)
def before_create_like(sender, instance, **kwargs):
    if instance.pk is None:  # Only for new likes
        Recipe.objects.filter(id=instance.recipe.id).update(
            likes=models.F('likes') + 1
        )

# Before deleting a like
@receiver(pre_delete, sender=RecipeLike)
def before_delete_like(sender, instance, **kwargs):
    Recipe.objects.filter(id=instance.recipe.id).update(
        likes=models.Case(
            models.When(likes__gt=0, then=models.F('likes') - 1),
            default=0,
            output_field=models.PositiveIntegerField()
        )
    )
