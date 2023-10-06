from django.forms import ModelForm
from .models import User

from django import forms

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


    