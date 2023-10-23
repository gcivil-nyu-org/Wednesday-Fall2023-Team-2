from django.test import TestCase
from django.urls import reverse
from .models import User
from django.contrib.auth.forms import AuthenticationForm


class LoginTests(TestCase):
    def setUp(self):
        """creates user with sample credentials
        """
        self.username = "parkrowd"
        self.email = "parkrowd@gmail.com"
        self.password = "iLikeParking123!"

        self.login_path_name = "users:login"
        self.welcome_path_name = "users:welcome"
        self.profile_path_name = "users:profile"

        self.template = "login.html"

        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )

    def test_login_view(self):
        """checks if login page returns a 200 Status Code
           and the template 'login.html' is used
        """
        response = self.client.get(reverse(self.login_path_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login_with_username(self):
        """checks if login page correctly redirects (302 Status Code)
           to the profile page of the user
           with correct username and password
        """
        response = self.client.post(reverse(self.login_path_name), {
            "username": self.email, 
            "password": self.password
            })
        self.assertRedirects(response, reverse(self.profile_path_name, args=[self.username]))

    def test_successful_login_with_email(self):
        """checks if login page correctly redirects (302 Status Code)
           to the profile page of the user
           with correct email and password
        """
        response_with_username = self.client.post(reverse(self.login_path_name), {
            "username": self.username, 
            "password": self.password
            })
        self.assertRedirects(response_with_username, reverse(self.profile_path_name, args=[self.username]))

    def test_unsuccessful_login(self):
        """checks if login page has the following...
           
           returns Status 200
           form contains 'credential invalid' type of message
        """

        dummy_password = "noParkingForYou"

        response = self.client.post(reverse("users:login"), {"username": self.username, "password": dummy_password})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, AuthenticationForm)
        self.assertContains(response, "The credentials you provided do not match any user.")