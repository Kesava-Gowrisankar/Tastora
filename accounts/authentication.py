from django.contrib.auth.models import User
from django.db.models import Q

class UsernameOrEmailLogin:
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.filter(
            Q(username__iexact=username) |
            Q(email__iexact=username)
        ).first()

        if user and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
