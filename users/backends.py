from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameAuthenticationBackend(object):
    @staticmethod
    def authenticate(request, username=None, password=None):
        """
        Returns User object if 
            1.  username or email match 
            2.  password match
        Else None
        """
        user = EmailOrUsernameAuthenticationBackend.get_user_by_username_or_email(username)
        if user and check_password(password, user.password):
            return user

        return None

    @staticmethod
    def get_user_by_username_or_email(field):
        """Helper function for authenticate method above"""
        try:
            return User.objects.get( Q(username=field) | Q(email=field) )
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
