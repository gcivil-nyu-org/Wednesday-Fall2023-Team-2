"""user forms

Creating Model Forms
https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

Difference between Model and Forms
https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms
"""

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
)

from users.models import Post


class CreatePostForm(UserCreationForm):
    """create post form"""

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Please give your post a title",
            }
        )
    )

    post = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Please enter your post"}
        )
    )

    class Meta:
        model = Post
        fields = ["title", "post"]
