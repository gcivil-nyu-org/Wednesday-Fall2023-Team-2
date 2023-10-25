"""user forms

Creating Model Forms
https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

Difference between Model and Forms
https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

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
    business_name = forms.CharField(max_length=200)
    business_type = forms.CharField(max_length=200)
    business_address = forms.CharField(max_length=200)
    uploaded_file = forms.FileField(
        label="Choose a file",
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx", "png", "jpg", "jpeg"])],
    )

    class Meta:
        model = UserVerification
        fields = ["business_name", "business_type", "business_address", "uploaded_file"]

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data["uploaded_file"]
        if not uploaded_file:
            raise forms.ValidationError("You must upload a file.")
        return uploaded_file
