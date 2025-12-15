from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel
import os

def user_profile_upload_to(instance, filename):
    return f"{instance.user.id}/profile/{filename}"


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to=user_profile_upload_to, blank=True, null=True, default='default.png')
    bio = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.user)

    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return os.path.join(settings.MEDIA_URL, 'default.png')


class Recipe(TimeStampedModel):
    class CategoryTypes(models.IntegerChoices):
        VEG = 0, "Veg"
        VEGAN = 1, "Vegan"
        NON_VEG = 2, "Non-Veg"

    class DifficultyLevels(models.IntegerChoices):
        EASY = 0, "Easy"
        MEDIUM = 1, "Medium"
        HARD = 2, "Hard"

    title = models.CharField(max_length=200)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    category = models.PositiveIntegerField(choices=CategoryTypes.choices, default=CategoryTypes.VEG)
    cuisine = models.CharField(max_length=50)
    difficulty = models.PositiveIntegerField(choices=DifficultyLevels.choices, default=DifficultyLevels.EASY)
    servings = models.PositiveIntegerField(default=1, help_text="Number of people the recipe serves")
    prep_time = models.PositiveIntegerField(help_text="Time required to prepare ingredients in minutes")
    total_time = models.PositiveIntegerField(help_text="Preparation time + Cooking Time in minutes",
                                             validators=[MaxValueValidator(300), MinValueValidator(5)])
    instructions = models.TextField()
    featured = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RecipeLike', related_name='liked_recipes', blank=True)

    def default_recipe_image_url(self):
        default_image = 'default-recipe.jpg'
        return f"{settings.MEDIA_URL}{default_image}"
    
    def get_first_image_url(self):
        latest_image = self.images.all().last()
        if latest_image and latest_image.image:
            return latest_image.image.url
        return self.default_recipe_image_url()
    
    
    def get_second_image_url(self):
        image = self.images.order_by('created')

        if image.count() > 1 and image[1].image:
            return image[1].image.url
        return self.default_recipe_image_url()

    def get_remaining_image(self):
        images = self.images.order_by('-created')[2:]
        return images if images.exists() else None

    def get_absolute_url(self):
        return reverse('recipe_management:recipe_detail', kwargs={'pk': self.pk})
    
    def difficulty_display(self):
        return {0: 'Easy', 1: 'Medium', 2: 'Hard'}.get(self.difficulty, 'Unknown')

    def prep_time_display(self):
        return f"{self.prep_time} min"

    def total_time_display(self):
        return f"{self.total_time} min"
    
    def total_likes(self):
        return self.likes

    def is_liked_by_user(self, user):
        return self.liked_by.filter(pk=user.pk).exists()

    class Meta:
        ordering = ("-created", "title")
        unique_together = ('title', 'author')
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.title

    def clean(self):
        if self.prep_time is not None and self.total_time is not None:
            if self.total_time < self.prep_time:
                raise ValidationError("Total time cannot be less than prep time.")
           

class RecipeLike(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipe_likes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_likes')

    class Meta:
        unique_together = ('user', 'recipe')
        ordering = ['-created']

    def __str__(self):
        return f"{self.user} liked {self.recipe}"

class Nutrition(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name='nutrition')
    calories = models.PositiveIntegerField(help_text="Estimated calories per serving")
    protein = models.PositiveIntegerField(help_text="Estimated protein per serving")
    fat = models.PositiveIntegerField(help_text="Estimated fat per serving")
    sugar = models.PositiveIntegerField(help_text="Estimated sugar per serving")
    fiber = models.PositiveIntegerField(help_text="Estimated fiber per serving")
    carbohydrates = models.PositiveIntegerField(help_text="Estimated carbohydrates per serving")

    def __str__(self):
        return f'Nutrition of {self.recipe}'


class Ingredient(models.Model):
    class UnitTypes(models.IntegerChoices):
        GRAM = 0, "grams"
        KILOGRAM = 1, "kilogram"
        TEASPOON = 2, "teaspoon"
        TABLESPOON = 3, "tablespoon"
        CUP = 4, "cup"
        PIECE = 5, "piece"

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.IntegerField(choices=UnitTypes.choices, default=UnitTypes.GRAM)
    optional = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Collection(TimeStampedModel):
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    recipes = models.ManyToManyField(Recipe, blank=True)

    class Meta:
        ordering = ('-created', 'title')
        unique_together = ('title', 'owner')

    def __str__(self):
        return self.title


def recipe_image_upload_to(instance, filename):
    safe_title = "".join(c if c.isalnum() else "_" for c in instance.recipe.title)
    return f"{instance.recipe.author.id}/recipe/{safe_title}/{filename}"


class RecipeImage(TimeStampedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=recipe_image_upload_to, default='default-recipe.jpg', blank=True, null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Image for recipe: {self.recipe.title}"
