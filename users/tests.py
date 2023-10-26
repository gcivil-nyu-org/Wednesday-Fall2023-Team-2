from django.test import TestCase
from django.urls import reverse

from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserVerification
from .forms import UserVerificationForm
from users.models import User

# Create your tests here.


class UserVerificationViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username="testuser", email="test@email.com", password="testpassword"
        )

    def test_get_request(self):
        # Test GET request to the view
        response = self.client.get(reverse("users:verification", args=["testuser"]))
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertTemplateUsed(
            response, "verification.html"
        )  # Ensure the correct template is used
        self.assertEqual(
            response.context["user"], self.test_user
        )  # Ensure user context variable is set

    def test_post_valid_request(self):
        # Test POST request with valid data
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type",
            "business_address": "123 Test St",
            "uploaded_file": SimpleUploadedFile("testfile.pdf", b"Test file content"),
        }
        response = self.client.post(
            reverse("users:verification", args=["testuser"]), data, follow=True
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse("users:profile", args=["testuser"])
        )  # Ensure redirection

        # Ensure that the verification object is created
        self.assertTrue(
            UserVerification.objects.filter(username=self.test_user).exists()
        )

    def test_post_invalid_request(self):
        # Test POST request with invalid data
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type",
            # Missing 'business_address' and 'uploaded_file'
        }
        response = self.client.post(
            reverse("users:verification", args=["testuser"]), data, follow=True
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse("users:profile", args=["testuser"])
        )  # Ensure redirection
        messages = list(response.context["messages"])
        self.assertTrue(messages)  # Ensure there are messages
        self.assertEqual(
            str(messages[0]),
            "Please resubmit the application with all necessary fields.",
        )

    def test_model_creation(self):
        # Test model creation based on valid form data
        data = {
            "business_name": "Test Business",
            "business_type": "Test Type",
            "business_address": "123 Test St",
        }
        uploaded_file = SimpleUploadedFile("testfile.pdf", b"Test file content")
        form = UserVerificationForm(data=data, files={"uploaded_file": uploaded_file})
        self.assertTrue(form.is_valid())

        # Create a UserVerification instance based on the form data
        verification = form.save(commit=False)
        verification.username = self.test_user
        verification.save()

        # Ensure that the verification object is created
        self.assertTrue(
            UserVerification.objects.filter(username=self.test_user).exists()

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
