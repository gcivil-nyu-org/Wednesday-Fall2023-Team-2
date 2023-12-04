"""map forms

Creating Model Forms
https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/

Difference between Model and Forms
https://stackoverflow.com/questions/5481713/whats-the-difference-between-django-models-and-forms
"""

from django import forms
import django.core.validators

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

    """
    For now, not used. Could potentially calculate in views.py using reverse geolocation lookup.
    address_zip = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Zip Code goes here",
            }
        )
    )
    """

    PARKING_SPACE_TYPES = [("Business", "Business"), ("Street", "Street"), ("Private", "Private")]

    BOROUGHS = [
        ("Manhattan", "Manhattan"),
        ("Brooklyn", "Brooklyn"),
        ("Queens", "Queens"),
        ("Bronx", "Bronx"),
        ("Staten Island", "Staten Island"),
    ]

    parking_spot_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Spot name goes here",
            }
        )
    )

    type = forms.ChoiceField(
        choices=PARKING_SPACE_TYPES,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Street or Business",
            }
        ),
    )

    borough = forms.ChoiceField(
        choices=BOROUGHS,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Borough goes here",
            }
        ),
    )

    detail = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Spot details go here"}
        )
    )

    operation_hours = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Any information on operational hours goes here",
            }
        )
    )

    occupancy_percent = forms.IntegerField(
        validators=[
            django.core.validators.MinValueValidator(0),
            django.core.validators.MaxValueValidator(100),
        ],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Please give an occupancy between 0 and 100 Percent",
            }
        ),
    )

    vehicle_spaces_capacity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Max number of vehicle parking spaces",
            }
        ),
    )

    class Meta:
        model = ParkingSpace
        fields = [
            "parking_spot_name",
            "type",
            "borough",
            "detail",
            "operation_hours",
            "occupancy_percent",
            "vehicle_spaces_capacity"
        ]
