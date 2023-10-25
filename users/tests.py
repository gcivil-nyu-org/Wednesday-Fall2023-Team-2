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
WELCOME_PATH_NAME = "users:welcome"
PROFILE_PATH_NAME = "users:profile"

LOGIN_TEMPLATE = "login.html"
REGISTER_TEMPLATE = "register.html"
WELCOME_TEMPLATE = "welcome.html"
PROFILE_TEMPLATE = "profile.html"


class LoginTests(TestCase):
    def setUp(self):
        """creates user with sample credentials"""

        self.user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )

    def test_login_view(self):
        """checks if login page returns a 200 Status Code
        and the template 'login.html' is used
        """
        response = self.client.get(reverse(LOGIN_PATH_NAME))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, LOGIN_TEMPLATE)

    def test_successful_login_with_username(self):
        """checks if login page correctly redirects (302 Status Code)
        to the profile page of the user
        with correct username and password
        """
        response = self.client.post(
            reverse(LOGIN_PATH_NAME),
            {"username": USERNAME, "password": PASSWORD},
        )
        self.assertRedirects(response, reverse(PROFILE_PATH_NAME, args=[USERNAME]))

    def test_successful_login_with_email(self):
        """checks if login page correctly redirects (302 Status Code)
        to the profile page of the user
        with correct email and password
        """
        response_with_username = self.client.post(
            reverse(LOGIN_PATH_NAME),
            {"username": EMAIL, "password": PASSWORD},
        )
        self.assertRedirects(
            response_with_username,
            reverse(PROFILE_PATH_NAME, args=[USERNAME]),
        )

    def test_remember_me_login(self):
        """checks if login page correctly redirects (302 Status Code)
        to the profile page of the user
        and the session cookie expiration is set to be > 1 day
        """

        response = self.client.post(
            reverse(LOGIN_PATH_NAME),
            {"username": USERNAME, "password": PASSWORD, "remember_me": "on"},
        )
        self.assertRedirects(
            response,
            reverse(PROFILE_PATH_NAME, args=[USERNAME]),
        )

        session_cookie = response.cookies.get("sessionid")
        self.assertTrue(session_cookie)

        session_expiry = dateutil.parser.parse(session_cookie.get("expires"))
        minimum_expiration = timezone.now() + timedelta(days=1)

        self.assertGreater(session_expiry.timestamp(), minimum_expiration.timestamp())

    def test_unsuccessful_login(self):
        """checks if login page has the following...

        returns Status 200
        form contains 'credential invalid' type of message
        """

        response = self.client.post(
            reverse(LOGIN_PATH_NAME),
            {"username": USERNAME, "password": DUMMY_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, AuthenticationForm)
        self.assertContains(
            response, "The credentials you provided do not match any user."
        )
