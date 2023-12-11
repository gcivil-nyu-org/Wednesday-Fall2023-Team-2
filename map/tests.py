from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import User, Post, UserVerification
from .models import ParkingSpace, OccupancyHistory
from .views import ParkingSpaceView
from .forms import CreateParkingSpaceForm

import json

USERNAME = "parkrowd"
EMAIL = "parkrowd@gmail.com"
PASSWORD = "iLikeParking123!"
DUMMY_PASSWORD = "noParkingForYou"

PARKING_SPOT_ID = "12657"
ADDRESS_ZIP = "10001"
LONGITUDE = "-73.9853043125"
LATITUDE = "40.7486538125"
PARKING_SPOT_NAME = "Empire State Building"

TITLE = "Parking Here For 15 Minutes"
POST = "After 3:15, I'll be gone."
DATE = timezone.now()

POST_PATH_NAME = "map:post"
ADD_SPOT_PATH_NAME = "map:add-parking-space"
REDIRECT_SPOT_PATH_NAME = "map:spot-redirect"
PEAK_TIME_PATH_NAME = "map:peak-time"
MAP_PATH_NAME = "map:parking"
POST_TEMPLATE = "map/post.html"


class CreatePostTests(TestCase):
    def setUp(self):
        # Create a test user and test spot
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

    def test_post_view(self):
        """checks if post page returns a 200 status code
        and the template 'map/post.html' is used
        """
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(reverse(POST_PATH_NAME, args=[PARKING_SPOT_ID]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, POST_TEMPLATE)

    def test_successful_post(self):
        """checks if post is made successfully
        and redirects (Status 302) to Map Page
        """
        self.client.login(username=USERNAME, password=PASSWORD)
        post_data = {"title": TITLE, "post": POST, "created_at": DATE}
        response = self.client.post(
            reverse(POST_PATH_NAME, args=[PARKING_SPOT_ID]), post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(title=TITLE).exists())

    def test_unsuccessful_post_invalid_data(self):
        """check if user tries to submit empty post form"""
        self.client.login(username=USERNAME, password=PASSWORD)
        post_data = {"title": "", "post": "", "created_at": DATE}
        response = self.client.post(
            reverse(POST_PATH_NAME, args=[PARKING_SPOT_ID]), post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "title", "This field is required.")
        self.assertFormError(response, "form", "post", "This field is required.")

class PeakTimeViewTests(TestCase):
    def setUp(self):
        # Create a test user, test spot, and test occupancy_history
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
    def test_get_view(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response_no_history = self.client.get(
            reverse(PEAK_TIME_PATH_NAME, args=[PARKING_SPOT_ID])
        )
        self.assertEqual(response_no_history.status_code, 200)
        content = json.loads(response_no_history.content)
        self.assertEqual(content.get('peak_time'), 'Not enough past data.')

        self.test_occupancy_history = OccupancyHistory.objects.create(
            user=self.test_user,
            parking_space=self.test_spot,
            occupancy_percent=80,
            updated_at="2023-12-11 14:33:18.596491"
        )
        response_history = self.client.get(
            reverse(PEAK_TIME_PATH_NAME, args=[PARKING_SPOT_ID])
        )

        self.assertEqual(response_history.status_code, 200)
        content = json.loads(response_history.content)
        self.assertEqual(content.get('peak_time'), "14 o'clock")