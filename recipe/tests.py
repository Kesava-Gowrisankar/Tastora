from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from recipe.models import Recipe

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
      