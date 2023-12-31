"""customized user manager
"""
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom User Manager Model to allow username
    and email to be unique identifiers for authentication
    """

    def create_user(
        self, email: str, username: str, password: str, **extra_fields: dict[str, any]
    ):
        """method to create a normal user

        Returns:
            User: user model that has been created
        """
        if not email:
            raise ValueError(_("An Email is required"))
        if not username:
            raise ValueError(_("A Username is required"))
        if not password:
            raise ValueError(_("A Password is required"))

        # * From Django's Docs:
        # * Normalize the email address by lowercasing the domain part of it.
        email = self.normalize_email(email)

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)

        # * self._db is the default DB under DATABASES in settings.py
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email: str, username: str, password: str, **extra_fields: dict[str, any]
    ):
        """method to create a super user

        Returns:
            User: user model that has been created
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff set to True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser set to True"))

        user = self.create_user(
            email=email, username=username, password=password, **extra_fields
        )

        return user
