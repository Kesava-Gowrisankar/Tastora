from django.contrib.auth.models import User

class UsernameOrEmailLogin:
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to find user by case-insensitive username first
        user = User.objects.filter(username__iexact=username).first()
        if not user:
            # Fallback: try case-insensitive email
            user = User.objects.filter(email__iexact=username).first()

        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
