from django.contrib.auth.models import User

class Username_or_Email_Login:
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # If not found by username, try email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None

        # Check password
        if user.check_password(password):
            return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
       