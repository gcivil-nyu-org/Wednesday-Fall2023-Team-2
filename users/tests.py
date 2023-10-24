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

LOGIN_TEMPLATE = "login.html"
REGISTER_TEMPLATE = "register.html"
WELCOME_TEMPLATE = "welcome.html"
PROFILE_TEMPLATE = "profile.html"


class RegisterTests(TestCase):
    def test_registration_view(self):
        """checks if register page returns a 200 Status Code
        and the template 'register.html' is used
        """
        response = self.client.get(reverse(REGISTER_PATH_NAME))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, REGISTER_TEMPLATE)

    def test_successful_user_registration(self):
        """checks if user is registered successfully
        and redirects (Status 302) to Welcome Page
        """
        user_data = {
            "username": USERNAME,
            "email": EMAIL,
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        response = self.client.post(reverse(REGISTER_PATH_NAME), user_data)
        self.assertRedirects(response, reverse(WELCOME_PATH_NAME))

        self.assertTrue(User.objects.filter(username=USERNAME).exists())

    def test_unsuccessful_user_registration_existing(self):
        """creates user and checks if a new account
        cannot be made with the existing username or email
        """
        User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)

        user_data = {
            "username": USERNAME,
            "email": EMAIL,
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        response = self.client.post(reverse(REGISTER_PATH_NAME), user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User with this Username already exists.")

        # * Change username entered into form for testing existing email
        user_data["username"] = "OTHER" + USERNAME
        response = self.client.post(reverse(REGISTER_PATH_NAME), user_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User with this Email already exists.")

    def test_unsuccessful_user_registration_invalid_data(self):
        """checks if user tries to submit empty register form"""
        user_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(reverse(REGISTER_PATH_NAME), user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "email", "This field is required.")
        self.assertFormError(response, "form", "password1", "This field is required.")
        self.assertFormError(response, "form", "password2", "This field is required.")
