from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from Tastora.recipe.domains import create_recipe_with_details
from recipe.models import Recipe, Ingredient, Nutrition, RecipeImage
import copy

class CreateRecipeDomainFunctionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='domainuser',
            password='password'
        )

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

    def test_domain_creates_recipe_successfully(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=[],
        )

        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertEqual(recipe.author, self.user)
        self.assertTrue(Nutrition.objects.filter(recipe=recipe).exists())

    def test_domain_creates_recipe_with_image(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={'image': self.image},
            ingredients_data=[],
        )

        recipe = Recipe.objects.get(title='Domain Recipe')
        self.assertTrue(
            RecipeImage.objects.filter(recipe=recipe).exists()
        )

    def test_domain_creates_multiple_ingredients(self):
        ingredients_data = [
            {
                'name': 'Tomato',
                'quantity': 100,
                'unit': '0',
                'optional': False,
            },
            {
                'name': 'Cheese',
                'quantity': 50,
                'unit': '0',
                'optional': True,
            },
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

    def test_domain_optional_ingredient_defaults_false(self):
        ingredients_data = [
            {
                'name': 'Salt',
                'quantity': 1,
                'unit': '0',
                # optional missing
            }
        ]

        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=ingredients_data,
        )

        ingredient = Ingredient.objects.get(name='Salt')
        self.assertFalse(ingredient.optional)

    def test_domain_quantity_defaults_to_zero(self):
        ingredients_data = [
            {
                'name': 'Pepper',
                'quantity': None,
                'unit': '0',
                'optional': False,
            }
        ]

        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=ingredients_data,
        )

        ingredient = Ingredient.objects.get(name='Pepper')
        self.assertEqual(ingredient.quantity, 0)

    def test_domain_creates_nutrition_correctly(self):
        create_recipe_with_details(
            user=self.user,
            recipe_data=self.recipe_data,
            nutrition_data=self.nutrition_data,
            image_data={},
            ingredients_data=[],
        )

        nutrition = Nutrition.objects.get(recipe__title='Domain Recipe')
        self.assertEqual(nutrition.calories, 250)
        self.assertEqual(nutrition.protein, 15)
