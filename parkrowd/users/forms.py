from django.forms import ModelForm
from .models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm

#Difference between Model and Forms
# https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms

#Creating Model Forms
# https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

class UserLoginForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["username", "password"]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'Enter username or email'
                }
            ),
            'password': forms.TextInput(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'Enter Password'
                }
            )
        }

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    