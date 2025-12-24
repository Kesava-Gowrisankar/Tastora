from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .domains import create_recipe_with_details, update_recipe_with_details
from .models import Collection, Recipe, Ingredient, Nutrition, RecipeImage, RecipeLike

# -------------------------
# Mixin for common test data
# -------------------------
class RecipeTestDataMixin:
    """
    Provides test data for recipes, users, ingredients, nutrition, images, and collections.
    """

    @classmethod
    def setUpTestData(cls):
        # Users
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.other_user = User.objects.create_user(username='otheruser', password='testpass123')

        # Recipe
        cls.recipe = Recipe.objects.create(
            title='Test Recipe',
            category='0',
            cuisine='Italian',
            difficulty='0',
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
            unit='0',
            optional=False
        )
        cls.ingredient2 = Ingredient.objects.create(
            recipe=cls.recipe,
            name='Cheese',
            quantity=50,
            unit='0',
            optional=True
        )

        # Recipe Image
        cls.image = RecipeImage.objects.create(
            recipe=cls.recipe,
            image=SimpleUploadedFile(name='test.jpg', content=b'\x47\x49\x46', content_type='image/jpeg')
        )

        # Collection
        cls.collection = Collection.objects.create(
            name='My Collection',
            owner=cls.user
        )

        # Simple uploaded image for domain tests
        cls.domain_image = SimpleUploadedFile(name='domain_test.jpg', content=b'\x47\x49\x46', content_type='image/jpeg')

# -------------------------
# CreateRecipeDomainFunctionTestCase
# -------------------------
class CreateRecipeDomainFunctionTestCase(TestCase, RecipeTestDataMixin):

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

    def test_domain_creates_recipe_successfully(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=[]
        )
        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertTrue(Nutrition.objects.filter(recipe=recipe).exists())

    def test_domain_creates_recipe_with_image(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={'image': self.domain_image},
            ingredients_data=[]
        )
        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertTrue(RecipeImage.objects.filter(recipe=recipe).exists())

# -------------------------
# UpdateRecipeDomainFunctionTestCase
# -------------------------
class UpdateRecipeDomainFunctionTestCase(TestCase, RecipeTestDataMixin):

    def setUp(self):
        # Existing ingredients for update tests
        self.ing1 = Ingredient.objects.create(recipe=self.recipe, name='Salt', quantity=1, unit='0', optional=False)
        self.ing2 = Ingredient.objects.create(recipe=self.recipe, name='Oil', quantity=2, unit='0', optional=False)

    def test_domain_updates_recipe_fields(self):
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

    def test_domain_creates_new_ingredient(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[{'name': 'Pepper', 'quantity': 1, 'unit': '0', 'optional': False}]
        )
        self.assertTrue(Ingredient.objects.filter(recipe=self.recipe, name='Pepper').exists())

# -------------------------
# RecipeDetailViewTestCase
# -------------------------
class RecipeDetailViewTestCase(TestCase, RecipeTestDataMixin):

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        self.url = reverse('recipe:recipe_detail', kwargs={'pk': self.recipe.pk})

    def test_detail_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_recipe(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)
        self.assertEqual(response.context['nutrition'], self.nutrition)
        self.assertIn(self.ingredient1, response.context['ingredients'])
        self.assertIn(self.ingredient2, response.context['ingredients'])
        self.assertEqual(response.context['first_img'], self.recipe.get_first_image_url())

# -------------------------
# RecipeCollectionViewsTest
# -------------------------
class RecipeCollectionViewsTest(TestCase, RecipeTestDataMixin):

    def setUp(self):
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_add_to_collection_page_loads(self):
        url = reverse('recipe:add_to_collection', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recipe.title)

    def test_toggle_add_recipe_to_collection(self):
        url = reverse('recipe:toggle_collection_membership', args=[self.recipe.id, self.collection.id])
        self.client.post(url)
        self.assertIn(self.recipe, self.collection.recipes.all())

    def test_delete_collection_view(self):
        url = reverse('recipe:delete_collection', args=[self.collection.id])
        self.client.post(url)
        self.assertFalse(Collection.objects.filter(id=self.collection.id).exists())
