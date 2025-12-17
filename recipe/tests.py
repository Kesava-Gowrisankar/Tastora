from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from recipe.models import Ingredient, Nutrition, Recipe, RecipeImage

class AddRecipeTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.url = reverse('recipe:create_recipe')

    def test_add_recipe_success(self):
        # Create a simple image file
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
            content_type='image/jpeg'
        )

        data = {
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
            'image': image,
            # Ingredient Formset data
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

        response = self.client.post(self.url, data, follow=True)

        # Check for success message
        self.assertContains(response, "🎉 Recipe created successfully!")

        # Check that the recipe was actually created
        self.assertTrue(Recipe.objects.filter(title='Test Recipe').exists())
    
class RecipeDetailViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a test recipe
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            category=0,  # Assuming choices exist
            difficulty=0,
            cuisine='Italian',
            servings=2,
            prep_time=10,
            total_time=20,
            instructions='Mix ingredients. Cook for 10 minutes.'
        )

        # Create Nutrition object
        self.nutrition = Nutrition.objects.create(
            recipe=self.recipe,
            calories=300,
            protein=10,
            fat=5,
            sugar=8,
            fiber=4,
            carbohydrates=40
        )

        # Create Ingredients
        self.ingredient1 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Tomato',
            quantity=100,
            unit=0,
            optional=False
        )
        self.ingredient2 = Ingredient.objects.create(
            recipe=self.recipe,
            name='Cheese',
            quantity=50,
            unit=0,
            optional=True
        )

        # Create Recipe Image
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
            content_type='image/jpeg'
        )
        self.recipe_image = RecipeImage.objects.create(
            recipe=self.recipe,
            image=self.image
        )

    def test_recipe_detail_view_status_code_and_template(self):
        url = reverse('recipe:recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Check correct template
        self.assertTemplateUsed(response, 'recipe/detail_recipe.html')

    def test_recipe_detail_view_context(self):
        url = reverse('recipe:recipe_detail', args=[self.recipe.id])
        response = self.client.get(url)
        context = response.context

        # Check context keys
        self.assertIn('recipe', context)
        self.assertIn('first_img', context)
        self.assertIn('nutrition', context)
        self.assertIn('ingredient', context)
        self.assertIn('instruction', context)

        # Check objects
        self.assertEqual(context['recipe'], self.recipe)
        self.assertEqual(context['nutrition'], self.nutrition)
        self.assertQuerysetEqual(
            context['ingredient'],
            [repr(self.ingredient1), repr(self.ingredient2)],
            ordered=False
        )

        # Check instructions splitting
        self.assertEqual(context['instruction'], ['Mix ingredients', 'Cook for 10 minutes'])

        # Check first image URL
        self.assertTrue(context['first_img'].endswith('test_image.jpg'))