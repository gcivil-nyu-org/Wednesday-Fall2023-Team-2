"""user forms

Creating Model Forms
https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

Difference between Model and Forms
https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms
"""

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    SetPasswordForm,
    UserCreationForm,
    PasswordResetForm,
    AuthenticationForm,
)

from .models import User, Post, UserVerification

from django.core.validators import FileExtensionValidator


class UserLoginForm(AuthenticationForm):
    """login form"""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username or email"}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        )
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "type": "checkbox"}
        ),
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.", code="inactive")

    class Meta:
        """_summary_"""

        model = User
        fields = ["username", "password"]


class UserRegisterForm(UserCreationForm):
    """user registration form"""

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username"}
        )
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter email"}
        )
    )

    """
    avatar = forms.ImageField(
        widget = forms.ClearableFileInput(
            attrs={"class": "form-control"}
        )
    )
    """

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter Password"}
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "post", "created_at"]


class UserVerificationForm(forms.ModelForm):
    BUSINESS_TYPES = (
        ("Public Parking Lot Owner", "Public Parking Lot Owner"),
        ("Private Parking Lot Owner", "Private Parking Lot Owner"), 
        ("Street Business Owner", "Street Business Owner"))
    business_name = forms.CharField(max_length=200)
    business_type = forms.ChoiceField(choices=BUSINESS_TYPES)
    business_address = forms.CharField(max_length=200)
    uploaded_file = forms.FileField(
        label="Choose a file",
        required=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "png", "jpg", "jpeg"]
            )
        ],
    )

    class Meta:
        model = UserVerification
        fields = ["business_name", "business_type", "business_address", "uploaded_file"]

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data["uploaded_file"]
        if not uploaded_file:
            raise forms.ValidationError("You must upload a file.")
        return uploaded_file


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
                "placeholder": "name@example.com",
            }
        )
    )

    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_email_subject.txt"

    class Meta:
        fields = ["email"]


class UserPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        strip=False,
        label="New password",
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter Password"}
        ),
    )
    new_password2 = forms.CharField(
        strip=False,
        label="New password confirmation",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        ),
    )

    class Meta:
        fields = ["new_password1", "new_password2"]
