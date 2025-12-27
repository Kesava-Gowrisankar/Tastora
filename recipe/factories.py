import factory
import random
from django.contrib.auth import get_user_model
from .models import Recipe, Nutrition, Ingredient, RecipeImage
from django.core.files.base import ContentFile

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')

class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    title = factory.Sequence(lambda n: f"Delicious Recipe {n}")
    author = factory.SubFactory(UserFactory)
    cuisine = factory.Faker('word')
    
    prep_time = factory.LazyFunction(lambda: random.randint(5, 60))
    
    @factory.lazy_attribute
    def total_time(self):
        extra_time = random.randint(5, 60)
        return min(self.prep_time + extra_time, 300)

    instructions = factory.Faker('paragraph', nb_sentences=5)
    category = factory.Iterator([Recipe.CategoryTypes.VEG, Recipe.CategoryTypes.VEGAN, Recipe.CategoryTypes.NON_VEG])
    difficulty = factory.Iterator([Recipe.DifficultyLevels.EASY, Recipe.DifficultyLevels.MEDIUM, Recipe.DifficultyLevels.HARD])
    servings = factory.LazyFunction(lambda: random.randint(1, 8))

class NutritionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Nutrition

    recipe = factory.SubFactory(RecipeFactory)
    
    calories = factory.LazyFunction(lambda: random.randint(100, 1200))
    protein = factory.LazyFunction(lambda: random.randint(0, 50))
    fat = factory.LazyFunction(lambda: random.randint(0, 50))
    sugar = factory.LazyFunction(lambda: random.randint(0, 30))
    fiber = factory.LazyFunction(lambda: random.randint(0, 20))
    carbohydrates = factory.LazyFunction(lambda: random.randint(0, 100))

class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    recipe = factory.SubFactory(RecipeFactory)
    name = factory.Faker('word')
    quantity = factory.LazyFunction(lambda: round(random.uniform(0.5, 500.0), 2))
    unit = factory.Iterator([choice[0] for choice in Ingredient.UnitTypes.choices])

class RecipeImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeImage

    recipe = factory.SubFactory(RecipeFactory)  # Replace 'yourapp' with your app name
    image = factory.LazyAttribute(lambda _: ContentFile(b'GIF87a', name='test.jpg'))