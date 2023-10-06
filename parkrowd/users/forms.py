from .models import User

from django import forms
from django.contrib.auth.forms import AuthenticationForm

#Difference between Model and Forms
# https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms

#Creating Model Forms
# https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username or email'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-control form-check-input', 'type': 'checkbox'})
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code="inactive",
            )

    class Meta:
        model = User
        fields = ["username", "password"]


    