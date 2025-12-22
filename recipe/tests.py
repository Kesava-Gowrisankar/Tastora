from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .domains import create_recipe_with_details, update_recipe_with_details
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
        response = self.client.get(self.url)
        ingredients = response.context['ingredients']
        self.assertIn(self.ingredient1, ingredients)
        self.assertIn(self.ingredient2, ingredients)
        self.assertEqual(ingredients.count(), 2)

    def test_instructions_split_into_list(self):
        response = self.client.get(self.url)
        response = self.client.get(self.url)
        instructions = response.context['instructions']
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
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['ingredients']), [])

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
        response = self.client.get(self.url)
        self.assertEqual(response.context['instructions'], [])

class UpdateRecipeDomainFunctionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='editdomainuser',
            password='password'
        )

        # ---------- Existing Recipe ----------
        self.recipe = Recipe.objects.create(
            title='Original Recipe',
            category='0',
            cuisine='Indian',
            difficulty='0',
            servings=2,
            prep_time=10,
            total_time=20,
            instructions='Old step.',
            author=self.user
        )

        # ---------- Existing Nutrition ----------
        self.nutrition = Nutrition.objects.create(
            recipe=self.recipe,
            calories=100,
            protein=10,
            fat=5,
            sugar=2,
            fiber=3,
            carbohydrates=20
        )

        # ---------- Existing Ingredients ----------
        self.ing1 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Salt',
            quantity=1,
            unit='0',
            optional=False
        )

        self.ing2 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Oil',
            quantity=2,
            unit='0',
            optional=False
        )

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

    def test_domain_updates_nutrition_fields(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={'calories': 300, 'protein': 25},
            image_data={},
            ingredients_data=[]
        )

        self.nutrition.refresh_from_db()
        self.assertEqual(self.nutrition.calories, 300)
        self.assertEqual(self.nutrition.protein, 25)

    def test_domain_updates_existing_ingredient(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[
                {
                    'id': self.ing1,
                    'name': 'Black Salt',
                    'quantity': 3,
                    'unit': '0',
                    'optional': True
                }
            ]
        )

        self.ing1.refresh_from_db()
        self.assertEqual(self.ing1.name, 'Black Salt')
        self.assertEqual(self.ing1.quantity, 3)
        self.assertTrue(self.ing1.optional)

    def test_domain_creates_new_ingredient(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[
                {
                    'name': 'Pepper',
                    'quantity': 1,
                    'unit': '0',
                    'optional': False
                }
            ]
        )

        self.assertTrue(
            Ingredient.objects.filter(recipe=self.recipe, name='Pepper').exists()
        )

    def test_domain_deletes_removed_ingredients(self):
        # Only ing1 submitted → ing2 should be deleted
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[
                {
                    'id': self.ing1,
                    'name': 'Salt',
                    'quantity': 1,
                    'unit': '0',
                    'optional': False
                }
            ]
        )

        self.assertTrue(
            Ingredient.objects.filter(id=self.ing1.id).exists()
        )
        self.assertFalse(
            Ingredient.objects.filter(id=self.ing2.id).exists()
        )

    def test_domain_quantity_defaults_to_zero(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[
                {
                    'name': 'Garlic',
                    'quantity': None,
                    'unit': '0',
                    'optional': False
                }
            ]
        )

        ingredient = Ingredient.objects.get(name='Garlic')
        self.assertEqual(ingredient.quantity, 0)

    def test_domain_optional_defaults_false(self):
        update_recipe_with_details(
            recipe=self.recipe,
            user=self.user,
            recipe_data={},
            nutrition_data={},
            image_data={},
            ingredients_data=[
                {
                    'name': 'Onion',
                    'quantity': 1,
                    'unit': '0',
                    # optional missing
                }
            ]
        )

        ingredient = Ingredient.objects.get(name='Onion')
        self.assertFalse(ingredient.optional)