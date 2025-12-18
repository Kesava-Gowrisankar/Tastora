from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from recipe.models import Recipe, Ingredient, Nutrition, RecipeImage
import copy

class CreateRecipeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.url = reverse('recipe:create_recipe')

        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
            content_type='image/jpeg'
        )

        # Base form data for recipe + nutrition + ingredient formset
        self.data = {
            'title': 'Test Recipe',
            'category': '0',  # Veg
            'cuisine': 'Italian',
            'difficulty': '0',  # Easy
            'servings': 2,
            'prep_time': 10,
            'total_time': 20,
            'instructions': 'Mix ingredients and cook.',
            'calories': 300,
            'protein': 10,
            'fat': 5,
            'sugar': 8,
            'fiber': 4,
            'carbohydrates': 40,
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-0-name': 'Tomato',
            'form-0-quantity': '100',
            'form-0-unit': '0',
            'form-0-optional': 'on',
            'form-1-name': 'Cheese',
            'form-1-quantity': '50',
            'form-1-unit': '0',
        }

    def test_create_recipe_success(self):
        """Test successful creation of recipe with all fields."""
        data = copy.deepcopy(self.data)
        data['image'] = self.image
        response = self.client.post(self.url, data, follow=True)

        self.assertContains(response, "Recipe created successfully!")
        recipe = Recipe.objects.get(title='Test Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.nutrition.calories, 300)
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertTrue(recipe.images.exists())

    def test_create_recipe_missing_title(self):
        """Test creation fails when required recipe title is missing."""
        data = copy.deepcopy(self.data)
        data.pop('title')
        response = self.client.post(self.url, data)
        self.assertContains(response, "Please correct the errors below.")
        self.assertFalse(Recipe.objects.exists())

    def test_create_recipe_missing_ingredients(self):
        """Test creation works even if no ingredients are submitted."""
        data = copy.deepcopy(self.data)
        data['form-TOTAL_FORMS'] = '0'
        data['form-INITIAL_FORMS'] = '0'
        # Remove ingredient fields
        keys_to_remove = [k for k in data if k.startswith('form-')]
        for key in keys_to_remove:
            data.pop(key)

        data['title'] = 'No Ingredient Recipe'
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, "Recipe created successfully!")
        recipe = Recipe.objects.get(title='No Ingredient Recipe')
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_create_recipe_without_image(self):
        """Test recipe can be created without an image."""
        data = copy.deepcopy(self.data)
        data.pop('image', None)
        data['title'] = 'No Image Recipe'

        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, "Recipe created successfully!")
        recipe = Recipe.objects.get(title='No Image Recipe')
        self.assertFalse(recipe.images.exists())

    def test_create_recipe_invalid_ingredient_quantity(self):
        """Test ingredient quantity invalid (non-numeric) triggers validation error."""
        data = copy.deepcopy(self.data)
        data['form-0-quantity'] = 'abc'
        response = self.client.post(self.url, data)
        self.assertContains(response, "Please correct the errors below.")
        self.assertFalse(Recipe.objects.exists())

    def test_create_recipe_unauthorized_access(self):
        """Test that unauthenticated user is redirected to login."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_recipe_partial_nutrition_data(self):
        """Test creation fails when nutrition data is incomplete."""
        data = copy.deepcopy(self.data)
        data.pop('calories')
        response = self.client.post(self.url, data)
        self.assertContains(response, "Please correct the errors below.")
        self.assertFalse(Recipe.objects.exists())

    def test_create_recipe_optional_ingredient_field(self):
        """Test creation succeeds when optional ingredient checkbox is unchecked."""
        data = copy.deepcopy(self.data)
        data['form-0-optional'] = ''  # optional unchecked
        data['title'] = 'Optional Ingredient Test'
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, "Recipe created successfully!")
        recipe = Recipe.objects.get(title='Optional Ingredient Test')
        self.assertEqual(recipe.ingredients.count(), 2)

    def test_create_recipe_multiple_ingredients(self):
        """Test creation with more than 2 ingredients."""
        data = copy.deepcopy(self.data)
        data['form-TOTAL_FORMS'] = '3'
        data['form-2-name'] = 'Onion'
        data['form-2-quantity'] = '30'
        data['form-2-unit'] = '0'
        response = self.client.post(self.url, data, follow=True)
        self.assertContains(response, "Recipe created successfully!")
        recipe = Recipe.objects.get(title='Test Recipe')
        self.assertEqual(recipe.ingredients.count(), 3)
