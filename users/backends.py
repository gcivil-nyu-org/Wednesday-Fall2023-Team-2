"""users app customized backends for authentication
"""
from typing import Optional
from django.db.models import Q
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

ActiveUserModel = get_user_model()


class EmailOrUsernameAuthenticationBackend(BaseBackend):
    def authenticate(
        self, request: HttpRequest, username: str = None, password: str = None
    ) -> Optional[ActiveUserModel]:
        """customized user auth method

        Args:
            request (django.http.HttpRequest): Http request object
            username (str, optional): username string. Defaults to None.
            password (str, optional): password string. Defaults to None.

        Returns:
            Optional[ActiveUserModel]: user object if the user could be found
        """
        user = self._get_user_by_username_or_email(username)
        if user and check_password(password, user.password):
            return user

        return None

    def _get_user_by_username_or_email(self, field: str) -> Optional[ActiveUserModel]:
        """helper method

        Args:
            field (str): username or email string

        Returns:
            Optional[ActiveUserModel]: user object if the user could be found
        """
        try:
            return ActiveUserModel.objects.get(Q(username=field) | Q(email=field))
        except ActiveUserModel.DoesNotExist:
            return None

    def get_user(self, user_id: str) -> Optional[ActiveUserModel]:
        """get user by primary key

        Args:
            user_id (str): user id/pk

        Returns:
            Optional[ActiveUserModel]: user object if the user could be found
        """
        try:
            return ActiveUserModel.objects.get(pk=user_id)
        except ActiveUserModel.DoesNotExist:
            return None
