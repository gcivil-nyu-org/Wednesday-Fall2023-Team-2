from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
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
        )
