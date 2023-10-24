from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm

import dateutil.parser

from django.utils import timezone
from datetime import timedelta

from .models import User
from .views import SESSION_COOKIE_EXPIRATION


USERNAME = "parkrowd"
EMAIL = "parkrowd@gmail.com"
PASSWORD = "iLikeParking123!"
DUMMY_PASSWORD = "noParkingForYou"

LOGIN_PATH_NAME = "users:login"
REGISTER_PATH_NAME = "users:register"
WELCOME_PATH_NAME = "users:welcome"
PROFILE_PATH_NAME = "users:profile"
LOGOUT_PATH_NAME = "users:logout"
PROFILE_DELETE_PATH_NAME = "users:profile_delete"

LOGIN_TEMPLATE = "login.html"
REGISTER_TEMPLATE = "register.html"
WELCOME_TEMPLATE = "welcome.html"
PROFILE_TEMPLATE = "profile.html"


class ProfileTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )
        # * Create a 2nd user with slightly different credentials
        self.user2_username = USERNAME + "2"
        self.user2_email = "2" + EMAIL

        self.user2 = User.objects.create_user(
            username=self.user2_username, email=self.user2_email, password=PASSWORD
        )

    def test_profile_view_not_logged_in(self):
        """checks if profile page returns a 200 Status Code,
        the template 'profile.html' is used,
        and a user profile can be viewed without logging in
        """
        response = self.client.get(reverse(PROFILE_PATH_NAME, args=[USERNAME]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PROFILE_TEMPLATE)

        self.assertEqual(response.context.get("is_user_owner_of_profile"), False)

    def test_profile_view_logged_in(self):
        """checks if profile page returns a 200 Status Code,
        the template 'profile.html' is used,
        and the logged in user can view their own profile
        """
        self.client.login(username=USERNAME, password=PASSWORD)

        response = self.client.get(reverse(PROFILE_PATH_NAME, args=[USERNAME]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PROFILE_TEMPLATE)

        self.assertEqual(response.context.get("is_user_owner_of_profile"), True)

    def test_logged_in_user_view_other_profile(self):
        """checks if profile page returns a 200 Status Code,
        the template 'profile.html' is used,
        and the logged in user can view their own profile
        """
        self.client.login(username=USERNAME, password=PASSWORD)

        response = self.client.get(
            reverse(PROFILE_PATH_NAME, args=[self.user2_username])
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context.get("is_user_owner_of_profile"), False)

    def test_profile_delete(self):
        """checks if logged in user can logout,
        the profile is deleted,
        and the user is redirect to the map
        """
        self.client.login(username=USERNAME, password=PASSWORD)

        response = self.client.post(
            reverse(PROFILE_DELETE_PATH_NAME, args=[USERNAME]), {"delete_profile": True}
        )
        self.assertFalse(User.objects.filter(username=USERNAME).exists())

        # TODO: Change to redirect to map view.  Currently will go to register
        self.assertRedirects(response, reverse(REGISTER_PATH_NAME))
