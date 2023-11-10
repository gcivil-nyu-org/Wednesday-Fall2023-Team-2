"""user forms

Creating Model Forms
https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

Difference between Model and Forms
https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms
"""

from django import forms

from users.models import Post
from map.models import ParkingSpace


class CreatePostForm(forms.ModelForm):
    """create post form"""

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Post title goes here",
            }
        )
    )

    post = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Post content goes here"}
        )
    )

    class Meta:
        model = Post
        fields = ["title", "post"]


class CreateParkingSpaceForm(forms.ModelForm):
    """create spot form"""

    details = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Spot details go here"}
        )
    )

    class Meta:
        model = ParkingSpace
        fields = ["details"]