from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .domains import create_recipe_with_details, update_recipe_with_details
from .models import (
    Recipe,
    Ingredient,
    Nutrition,
    RecipeImage,
    RecipeLike,
    Collection,
)

# ============================================================
# MIXIN: Shared test data (used by multiple test classes)
# ============================================================

class RecipeTestDataMixin:
    """
    Shared test data for users, recipes, ingredients,
    nutrition, images, and collections.
    """

    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Recipe
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            category=Recipe.CategoryTypes.VEG,
            cuisine='Italian',
            difficulty=Recipe.DifficultyLevels.EASY,
            servings=2,
            prep_time=10,
            total_time=20,
            instructions='Step 1. Step 2. Step 3.',
            author=cls.user
        )

        # Nutrition
        cls.nutrition = Nutrition.objects.create(
            recipe=cls.recipe,
            calories=200,
            protein=10,
            fat=5,
            sugar=8,
            fiber=3,
            carbohydrates=30
        )

        # Ingredients
        cls.ingredient1 = Ingredient.objects.create(
            recipe=cls.recipe,
            name='Tomato',
            quantity=100,
            unit=Ingredient.UnitTypes.GRAM,
            optional=False
        )
        cls.ingredient2 = Ingredient.objects.create(
            recipe=cls.recipe,
            name='Cheese',
            quantity=50,
            unit=Ingredient.UnitTypes.GRAM,
            optional=True
        )

        # Image
        cls.image = RecipeImage.objects.create(
            recipe=cls.recipe,
            image=SimpleUploadedFile(
                name='test.jpg',
                content=b'\x47\x49\x46',
                content_type='image/jpeg'
            )
        )

        # Collection
        cls.collection = Collection.objects.create(
            name='My Collection',
            owner=cls.user
        )

        # Reusable upload
        cls.uploaded_image = SimpleUploadedFile(
            name='domain_test.jpg',
            content=b'\x47\x49\x46',
            content_type='image/jpeg'
        )


# ============================================================
# DOMAIN: CREATE RECIPE
# ============================================================

class CreateRecipeDomainFunctionTestCase(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.recipe_data = {
            'title': 'Domain Recipe',
            'category': '0',
            'cuisine': 'Italian',
            'difficulty': '0',
            'servings': 2,
            'prep_time': 10,
            'total_time': 20,
            'instructions': 'Cook well.',
        }

        self.nutrition_data = {
            'calories': 250,
            'protein': 15,
            'fat': 10,
            'sugar': 5,
            'fiber': 3,
            'carbohydrates': 30,
        }

    def test_domain_creates_recipe(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=[]
        )

        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertEqual(recipe.author, self.user)

    def test_domain_creates_recipe_with_image(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={'image': self.uploaded_image},
            ingredients_data=[]
        )

        self.assertTrue(
            RecipeImage.objects.filter(recipe__title='Domain Recipe').exists()
        )


# ============================================================
# VIEW: RECIPE DETAIL
# ============================================================

class RecipeDetailViewTestCase(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('recipe:recipe_detail', kwargs={'pk': self.recipe.pk})

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_recipe(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_context_contains_nutrition(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['nutrition'], self.nutrition)

    def test_context_contains_ingredients(self):
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertEqual(ingredients.count(), 2)

    def test_instructions_split(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.context['instructions'],
            ['Step 1', 'Step 2', 'Step 3']
        )


# ============================================================
# DOMAIN: UPDATE RECIPE
# ============================================================

class UpdateRecipeDomainFunctionTestCase(RecipeTestDataMixin, TestCase):

    def test_updates_recipe_title(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={'title': 'Updated Recipe'},
            nutrition_data={},
            image_data={},
            ingredients_data=[]
        )

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Recipe')

    def test_updates_nutrition(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={'calories': 500},
            image_data={},
            ingredients_data=[]
        )

        self.nutrition.refresh_from_db()
        self.assertEqual(self.nutrition.calories, 500)


# ============================================================
# VIEWS: COLLECTION
# ============================================================

class RecipeCollectionViewsTest(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

    def test_add_to_collection_page(self):
        url = reverse('recipe:add_to_collection', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_toggle_add_recipe(self):
        url = reverse(
            'recipe:toggle_collection_membership',
            args=[self.recipe.id, self.collection.id]
        )
        self.client.post(url)
        self.assertIn(self.recipe, self.collection.recipes.all())

    def test_toggle_remove_recipe(self):
        self.collection.recipes.add(self.recipe)
        url = reverse(
            'recipe:toggle_collection_membership',
            args=[self.recipe.id, self.collection.id]
        )
        self.client.post(url)
        self.assertNotIn(self.recipe, self.collection.recipes.all())

    def test_user_cannot_delete_others_recipe(self):
        recipe = Recipe.objects.create(
            title='Other Recipe',
            author=self.other_user
        )
        url = reverse('recipe:delete_recipe', args=[recipe.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
