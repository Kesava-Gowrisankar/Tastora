from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from recipe.models import Profile
from recipe.forms import ProfileForm
from django.contrib.auth.models import User

class ProfileFormTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_profile_form_valid_data(self):
        # Create a dummy image file
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B',
            content_type='image/jpeg'
        )

        form_data = {
            'bio': 'This is a test bio.',
            'location': 'Test City',
        }
        form_files = {
            'profile_picture': image
        }

        form = ProfileForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        profile = form.save(commit=False)
        profile.user = self.user
        profile.save()

        # Check that the profile was saved correctly
        self.assertEqual(Profile.objects.count(), 1)
        saved_profile = Profile.objects.first()
        self.assertEqual(saved_profile.bio, 'This is a test bio.')
        self.assertEqual(saved_profile.location, 'Test City')
        self.assertTrue(saved_profile.profile_picture.name.endswith('test_image.jpg'))

    def test_profile_form_missing_data(self):
        # Only provide bio (location is optional in the model)
        form_data = {
            'bio': 'Bio only',
        }
        form = ProfileForm(data=form_data)
        self.assertTrue(form.is_valid())  # Assuming location and profile_picture are optional

        profile = form.save(commit=False)
        profile.user = self.user
        profile.save()

        saved_profile = Profile.objects.first()
        self.assertEqual(saved_profile.bio, 'Bio only')
        self.assertEqual(saved_profile.location, '')  # Should be empty string if not provided
        self.assertFalse(saved_profile.profile_picture)  # Should be empty

    def test_profile_form_invalid_data(self):
        # Example: upload invalid file type (not an image)
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is a text file, not an image.',
            content_type='text/plain'
        )
        form_data = {
            'bio': 'Bio',
            'location': 'City'
        }
        form_files = {
            'profile_picture': invalid_file
        }
        form = ProfileForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('profile_picture', form.errors)
