import dateutil.parser
from django.core import mail
from datetime import timedelta
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.tokens import default_token_generator

from users.models import User
from .models import (
    UserVerification,
    Post,
)
from parkrowd.settings import EMAIL_HOST_USER
from .views import UserPasswordResetConfirmView
from .forms import (
    UserVerificationForm,
    UserPasswordResetForm,
    UserPasswordResetConfirmForm,
)
from map.models import ParkingSpace

USERNAME = "parkrowd"
EMAIL = "parkrowd@gmail.com"
PASSWORD = "iLikeParking123!"
DUMMY_PASSWORD = "noParkingForYou"

LOGIN_PATH_NAME = "users:login"

LOGOUT_PATH_NAME = "users:logout"
WELCOME_PATH_NAME = "users:welcome"
PROFILE_PATH_NAME = "users:profile"
REGISTER_PATH_NAME = "users:register"
VERIFICATION_PATH_NAME = "users:verification"
PROFILE_DELETE_PATH_NAME = "users:profile-delete"
PASSWORD_RESET_PATH_NAME = "users:password-reset"
PASSWORD_RESET_CONFIRM_PATH_NAME = "users:password-reset-confirm"
PASSWORD_RESET_SUCCESS_PATH_NAME = "users:password-reset-success"
PASSWORD_RESET_EMAIL_SENT_PATH_NAME = "users:password-reset-email-sent"
EDIT_POST_PATH_NAME = "users:edit_post"

LOGIN_TEMPLATE = "users/login.html"
WELCOME_TEMPLATE = "users/welcome.html"
PROFILE_TEMPLATE = "users/profile.html"
REGISTER_TEMPLATE = "users/register.html"
VERIFICATION_TEMPLATE = "users/verification.html"
PASSWORD_RESET_TEMPLATE = "users/password_reset.html"
PASSWORD_RESET_CONFIRM_TEMPLATE = "users/password_reset_confirm.html"
PASSWORD_RESET_SUCCESS_TEMPLATE = "users/password_reset_success.html"
PASSWORD_RESET_EMAIL_SENT_TEMPLATE = "users/password_reset_email_sent.html"
EDIT_POST_TEMPLATE = "users/edit_post.html"

PARKING_SPOT_ID = "12657"
ADDRESS_ZIP = "10001"
LONGITUDE = "-73.9853043125"
LATITUDE = "40.7486538125"
PARKING_SPOT_NAME = "Empire State Building"
TEST_TITLE = "My Post"
TEST_POST = "This Spot is Great"
DATE_TIME = timezone.now()


class UserVerificationViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )

    def test_get_request(self):
        # Test GET request to the view
        response = self.client.get(reverse(VERIFICATION_PATH_NAME, args=[USERNAME]))
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertTemplateUsed(
            response, VERIFICATION_TEMPLATE
        )  # Ensure the correct template is used
        self.assertEqual(
            response.context["user"], self.test_user
        )  # Ensure user context variable is set

    def test_post_valid_request(self):
        # Test POST request with valid data
        data = {
            "business_name": "Test Business",
            "business_type": "Public Parking Lot Owner",
            "business_address": "123 Test St",
            "uploaded_file": SimpleUploadedFile("testfile.pdf", b"Test file content"),
        }
        response = self.client.post(
            reverse(VERIFICATION_PATH_NAME, args=[USERNAME]), data, follow=True
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse(PROFILE_PATH_NAME, args=[USERNAME])
        )  # Ensure redirection

        # Ensure that the verification object is created
        self.assertTrue(
            UserVerification.objects.filter(username=self.test_user).exists()
        )

    def test_post_invalid_request(self):
        # Test POST request with invalid data
        data = {
            "business_name": "Test Business",
            "business_type": "Public Parking Lot Owner",
            # Missing 'business_address' and 'uploaded_file'
        }
        response = self.client.post(
            reverse(VERIFICATION_PATH_NAME, args=[USERNAME]), data, follow=True
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse(PROFILE_PATH_NAME, args=[USERNAME])
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
            "business_type": "Public Parking Lot Owner",
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
        )


class RegisterTests(TestCase):
    def test_registration_view(self):
        """checks if register page returns a 200 Status Code
        and the template 'users/register.html' is used
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

        # * Change username entered into form for testing existing email
        user_data["username"] = "OTHER" + USERNAME
        response = self.client.post(reverse(REGISTER_PATH_NAME), user_data)
        self.assertEqual(response.status_code, 200)

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
        the template 'users/profile.html' is used,
        and a user profile can be viewed without logging in
        """
        response = self.client.get(reverse(PROFILE_PATH_NAME, args=[USERNAME]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PROFILE_TEMPLATE)

        self.assertEqual(response.context.get("is_user_owner_of_profile"), False)

    def test_profile_view_logged_in(self):
        """checks if profile page returns a 200 Status Code,
        the template 'users/profile.html' is used,
        and the logged in user can view their own profile
        """
        self.client.login(username=USERNAME, password=PASSWORD)

        response = self.client.get(reverse(PROFILE_PATH_NAME, args=[USERNAME]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PROFILE_TEMPLATE)

        self.assertEqual(response.context.get("is_user_owner_of_profile"), True)

    def test_logged_in_user_view_other_profile(self):
        """checks if profile page returns a 200 Status Code,
        the template 'users/profile.html' is used,
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
        and the template 'users/login.html' is used
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


class PasswordResetTests(TestCase):
    def setUp(self):
        """creates user with sample credentials"""
        self.user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )

    def test_password_reset_view(self):
        """checks if password reset page returns a 200 Status Code
        and the template 'users/password_reset.html' is used
        """
        response = self.client.get(reverse(PASSWORD_RESET_PATH_NAME))
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_TEMPLATE)

    def test_invalid_email(self):
        """checks if we can detect invalid emails, and ask the user to try again"""
        response = self.client.post(
            reverse(PASSWORD_RESET_PATH_NAME), {"email": "invalid@email"}
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_TEMPLATE)
        self.assertContains(response, "Enter a valid email address")

    def test_non_existent_email(self):
        """checks if we can detect emails that do not exist in database, and ask the user to try again"""
        response = self.client.post(
            reverse(PASSWORD_RESET_PATH_NAME), {"email": f"nonexisistent.{EMAIL}"}
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_TEMPLATE)
        self.assertContains(
            response,
            "This email does not match any of our records, please check for any typos",
        )

    def test_password_reset_redirect(self):
        """checks if redirect the user to password reset email sent page if everything goes as planned"""
        response = self.client.post(reverse(PASSWORD_RESET_PATH_NAME), {"email": EMAIL})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse(PASSWORD_RESET_EMAIL_SENT_PATH_NAME)
        )  # Ensure redirection


class PasswordResetEmailSentTests(TestCase):
    def test_password_reset_email_sent_view(self):
        """checks if password reset email sent page returns a 200 Status Code
        and the template 'users/password_reset_email_sent.html' is used
        """
        response = self.client.get(reverse(PASSWORD_RESET_EMAIL_SENT_PATH_NAME))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PASSWORD_RESET_EMAIL_SENT_TEMPLATE)


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        """creates user with sample credentials"""
        self.user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )

    def __get_user(self) -> User:
        """helper method that returns the user created"""
        return User.objects.get(username=USERNAME, email=EMAIL)

    def test_non_exisistent_user_uidb64(self):
        """check if we detects uidb64 that does not correspond to any user"""
        response = self.client.get(
            reverse(
                PASSWORD_RESET_CONFIRM_PATH_NAME,
                args=[
                    urlsafe_base64_encode(force_bytes(self.__get_user().pk + 100)),
                    "FAKETOKEN",
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetConfirmForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_CONFIRM_TEMPLATE)
        self.assertContains(
            response,
            "User not found. Please contact site admin if you believe this is an error.",
        )

    def test_fake_or_expired_token(self):
        """checks if we detect invalid or expired token"""
        response = self.client.get(
            reverse(
                PASSWORD_RESET_CONFIRM_PATH_NAME,
                args=[
                    urlsafe_base64_encode(force_bytes(self.__get_user().pk)),
                    "FAKETOKEN",
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetConfirmForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_CONFIRM_TEMPLATE)
        self.assertContains(
            response, "Your reset passsword URL is invalid or has expired"
        )

    def test_valid_reset_url(self):
        """checks if we recognize valid reset urls and redirect"""
        user = self.__get_user()
        response = self.client.get(
            reverse(
                PASSWORD_RESET_CONFIRM_PATH_NAME,
                args=[
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    default_token_generator.make_token(user),
                ],
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse(
                PASSWORD_RESET_CONFIRM_PATH_NAME,
                args=[
                    urlsafe_base64_encode(force_bytes(user.pk)),
                    UserPasswordResetConfirmView.reset_url_token,
                ],
            ),
        )
        form = response.context["form"]
        self.assertIsInstance(form, UserPasswordResetConfirmForm)
        self.assertTemplateUsed(response, PASSWORD_RESET_CONFIRM_TEMPLATE)


class PasswordResetSuccessTest(TestCase):
    def test_password_reset_success_view(self):
        """checks if password reset success page returns a 200 Status Code
        and the template 'users/password_reset_success.html' is used
        """
        response = self.client.get(reverse(PASSWORD_RESET_SUCCESS_PATH_NAME))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, PASSWORD_RESET_SUCCESS_TEMPLATE)


class EmailTest(TestCase):
    def test_send_email(self):
        test_subject = "Test Subject"
        test_message = "Test message"
        to_email = "to@test.com"
        mail.send_mail(
            test_subject,
            test_message,
            from_email=None,
            recipient_list=[to_email],
            fail_silently=False,
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], to_email)
        self.assertEqual(mail.outbox[0].body, test_message)
        self.assertEqual(mail.outbox[0].subject, test_subject)
        self.assertEqual(mail.outbox[0].from_email, EMAIL_HOST_USER)


class EditPostTest(TestCase):
    def setUp(self):
        # Create a test user, test post, and test spot
        self.test_user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )
        self.test_spot = ParkingSpace.objects.create(
            parking_spot_id=PARKING_SPOT_ID,
            address_zip=ADDRESS_ZIP,
            longitude=LONGITUDE,
            latitude=LATITUDE,
            parking_spot_name=PARKING_SPOT_NAME,
        )
        self.test_post = Post.objects.create(
            title=TEST_TITLE,
            post=TEST_POST,
            author=self.test_user,
            created_at=DATE_TIME,
            parking_space=self.test_spot,
        )

    def test_edit_post_get_view(self):
        """checks if edit post page returns a 200 Status Code
        and the template 'users/edit_post.html' is used
        """
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(
            reverse(EDIT_POST_PATH_NAME, args=[USERNAME, self.test_post.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, EDIT_POST_TEMPLATE)

    def test_post_valid_request(self):
        # Test POST request with valid data
        data = {
            "title": "test title",
            "post": "test post",
        }
        response = self.client.post(
            reverse(EDIT_POST_PATH_NAME, args=[USERNAME, self.test_post.pk]),
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse(PROFILE_PATH_NAME, args=[USERNAME])
        )  # Ensure redirection

        # Ensure that the post object was succesfully changed
        self.assertTrue(
            Post.objects.filter(
                pk=self.test_post.pk, title=data["title"], post=data["post"]
            ).exists()
        )

    def test_post_invalid_request(self):
        """***This test may need to change if we allow users to edit posts from the map page as well***"""
        self.client.login(username=USERNAME, password=PASSWORD)
        # Test POST request with invalid data
        data = {
            "title": "test title",
            "post": "",
        }
        response = self.client.post(
            reverse(EDIT_POST_PATH_NAME, args=[USERNAME, self.test_post.pk]),
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)  # Ensure the response is OK
        self.assertRedirects(
            response, reverse(EDIT_POST_PATH_NAME, args=[USERNAME, self.test_post.pk])
        )  # Ensure redirection

        # Ensure that the post has not changed
        self.assertTrue(
            Post.objects.filter(pk=self.test_post.pk, post=TEST_POST).exists()
        )
