from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .domains import create_recipe_with_details, update_recipe_with_details
from .models import Recipe, Ingredient, Nutrition, RecipeImage
from .mixins import RecipeTestDataMixin

class CreateRecipeDomainFunctionTestCase(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.user = self.create_test_user(username="domainuser")
        self.image = SimpleUploadedFile(
            name='domain_test.jpg',
            content=b'\x47\x49\x46',
            content_type='image/jpeg'
        )
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
        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertTrue(RecipeImage.objects.filter(recipe=recipe).exists())

    def test_domain_creates_multiple_ingredients(self):
        ingredients_data = [
            {'name': 'Tomato', 'quantity': 100, 'unit': '0', 'optional': False},
            {'name': 'Cheese', 'quantity': 50, 'unit': '0', 'optional': True},
        ]
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=ingredients_data,
        )
        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertEqual(recipe.ingredients.count(), 2)

class RecipeDetailViewTestCase(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.client = Client()
        self.user = self.create_test_user(username='detailuser')
        self.recipe = self.create_test_recipe(author=self.user, title='Detail Recipe')
        self.nutrition = self.create_test_nutrition(recipe=self.recipe)
        self.ingredient1 = self.create_test_ingredient(recipe=self.recipe, name='Tomato')
        self.ingredient2 = self.create_test_ingredient(recipe=self.recipe, name='Cheese')
        self.image = self.create_test_image(recipe=self.recipe)
        self.url = reverse('recipe:recipe_detail', kwargs={'pk': self.recipe.pk})

    def test_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_contains_recipe(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_context_contains_ingredients(self):
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertIn(self.ingredient1, ingredients)
        self.assertIn(self.ingredient2, ingredients)

class UpdateRecipeDomainFunctionTestCase(RecipeTestDataMixin, TestCase):

    def setUp(self):
        self.user = self.create_test_user(username='editdomainuser')
        self.recipe = self.create_test_recipe(author=self.user, title='Original Recipe')
        self.nutrition = self.create_test_nutrition(recipe=self.recipe, calories=100)
        self.ing1 = self.create_test_ingredient(recipe=self.recipe, name='Salt', quantity=1)
        self.ing2 = self.create_test_ingredient(recipe=self.recipe, name='Oil', quantity=2)

    def test_domain_updates_recipe_title(self):
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

    def test_domain_updates_existing_ingredient(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[{
                'id': self.ing1.id,
                'name': 'Black Salt',
                'quantity': 3,
                'unit': '0',
                'optional': True
            }]
        )
        self.ing1.refresh_from_db()
        self.assertEqual(self.ing1.name, 'Black Salt')
        self.assertEqual(self.ing1.quantity, 3)
        self.assertTrue(self.ing1.optional)
