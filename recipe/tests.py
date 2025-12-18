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

class RecipeDetailViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='detailuser', password='password')
        self.recipe = Recipe.objects.create(
            title='Detail Recipe',
            category='0',
            cuisine='Italian',
            difficulty='0',
            servings=2,
            prep_time=10,
            total_time=20,
            instructions='Step 1. Step 2. Step 3.',
            author=self.user
        )
        # Add nutrition
        self.nutrition = Nutrition.objects.create(
            recipe=self.recipe,
            calories=200,
            protein=10,
            fat=5,
            sugar=8,
            fiber=3,
            carbohydrates=30
        )

        # Add ingredients
        self.ingredient1 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Tomato',
            quantity=100,
            unit='0',
            optional=False
        )
        self.ingredient2 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Cheese',
            quantity=50,
            unit='0',
            optional=True
        )

        # Add image
        self.image = RecipeImage.objects.create(
            recipe=self.recipe,
            image=SimpleUploadedFile(
                name='test.jpg',
                content=b'\x47\x49\x46',
                content_type='image/jpeg'
            )
        )

        self.url = reverse('recipe:recipe_detail', kwargs={'pk': self.recipe.pk})

    def test_detail_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_detail_view_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe/detail_recipe.html')

    def test_context_contains_recipe(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['recipe'], self.recipe)

    def test_context_contains_first_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['first_img'], self.recipe.get_first_image_url())

    def test_context_contains_nutrition(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['nutrition'], self.nutrition)

    def test_context_contains_ingredients(self):
        response = self.client.get(self.url)
        ingredients = response.context['ingredient']
        self.assertIn(self.ingredient1, ingredients)
        self.assertIn(self.ingredient2, ingredients)
        self.assertEqual(ingredients.count(), 2)

    def test_instructions_split_into_list(self):
        response = self.client.get(self.url)
        instructions = response.context['instruction']
        # Should split by '.' and remove empty strings
        expected = ['Step 1', 'Step 2', 'Step 3']
        self.assertEqual(instructions, expected)

    def test_recipe_without_nutrition(self):
        recipe_no_nutrition = Recipe.objects.create(
            title='No Nutrition',
            category='0',
            cuisine='Italian',
            difficulty='0',
            servings=1,
            prep_time=5,
            total_time=10,
            instructions='Do something.',
            author=self.user
        )
        url = reverse('recipe:recipe_detail', kwargs={'pk': recipe_no_nutrition.pk})
        response = self.client.get(url)
        self.assertIsNone(response.context['nutrition'])

    def test_recipe_without_ingredients(self):
        recipe_no_ingredients = Recipe.objects.create(
            title='No Ingredients',
            category='0',
            cuisine='Italian',
            difficulty='0',
            servings=1,
            prep_time=5,
            total_time=10,
            instructions='Do something.',
            author=self.user
        )
        url = reverse('recipe:recipe_detail', kwargs={'pk': recipe_no_ingredients.pk})
        response = self.client.get(url)
        self.assertEqual(list(response.context['ingredient']), [])

    def test_recipe_without_images(self):
        recipe_no_image = Recipe.objects.create(
            title='No Image',
            category='0',
            cuisine='Italian',
            difficulty='0',
            servings=1,
            prep_time=5,
            total_time=10,
            instructions='Do something.',
            author=self.user
        )
        url = reverse('recipe:recipe_detail', kwargs={'pk': recipe_no_image.pk})
        response = self.client.get(url)
        self.assertIsNone(response.context['first_img'])

    def test_unauthenticated_user_can_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        # Detail view is accessible without login
        self.assertEqual(response.status_code, 200)

    def test_instructions_empty_string(self):
        recipe_empty_instr = Recipe.objects.create(
            title='Empty Instructions',
            category='0',
            cuisine='Italian',
            difficulty='0',
            servings=1,
            prep_time=5,
            total_time=10,
            instructions='',
            author=self.user
        )
        url = reverse('recipe:recipe_detail', kwargs={'pk': recipe_empty_instr.pk})
        response = self.client.get(url)
        self.assertEqual(response.context['instruction'], [])
