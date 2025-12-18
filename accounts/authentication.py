from django.contrib.auth.models import User
from django.db.models import Q

class UsernameOrEmailLogin:
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.filter(
            Q(username=username) |
            Q(email=username)
        ).first()

        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
