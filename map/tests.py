from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import User, Post, UserVerification
from .models import ParkingSpace
from .views import ParkingSpaceView
from .forms import CreateParkingSpaceForm


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
MAP_PATH_NAME = "map:parking"
POST_TEMPLATE = "map/post.html"

class MapViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD
        )
        self.user_verification = UserVerification.objects.create(
            username=self.user,
            status='verified'
        )

    def test_non_authenticated_user(self):
        response = self.client.get(
            reverse(MAP_PATH_NAME)
        )
        self.assertEqual(response.status_code, 200)

        # * Check if the user_verification is NOT present in the context
        self.assertIsNone(response.context.get('user_verification'))
        
    
    def test_authenticated_user(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.get(
            reverse(MAP_PATH_NAME)
        )
        self.assertEqual(response.status_code, 200)

        # * Check if the user_verification is present in the context
        self.assertIsNotNone(response.context.get('user_verification'))
    
class ParkingSpaceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD
        )
        self.user_verification = UserVerification.objects.create(
            username=self.user,
            status='verified'
        )

    def test_get_view(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        response_no_lat_lon = self.client.get(reverse(ADD_SPOT_PATH_NAME))
        self.assertEqual(response_no_lat_lon.status_code, 200)
        self.assertEqual(response_no_lat_lon.context.get('error'), "Unable to collect longitude and latitude from URL. Please check if the URL is correct.")
        self.assertIsNotNone(response_no_lat_lon.context.get('user_verification'))

        response_with_lat_lon = self.client.get(reverse(ADD_SPOT_PATH_NAME) + '?lat=10.123&lon=20.456')
        self.assertEqual(response_with_lat_lon.status_code, 200)
        self.assertIsNone(response_with_lat_lon.context.get('error'))
        self.assertIsNotNone(response_with_lat_lon.context.get('user_verification'))

    def test_get_next_parking_space_id(self):
        parking_space_view = ParkingSpaceView()
        id = parking_space_view._ParkingSpaceView__get_next_parkingspace_id()
        self.assertEqual(id, '1')

        # * Test if adding new record generates new ID of 2
        self.new_parking_spot = ParkingSpace.objects.create(parking_spot_id=1)
        id = parking_space_view._ParkingSpaceView__get_next_parkingspace_id()
        self.assertEqual(id, '2')

    def test_post_view(self):
        post_data = {"parking_spot_name": "TEST NAME", "type": "Street", "detail": "TEST DETAIL", "operation_hours": "TEST OP HRS", "occupancy_percent": 10}
        # * Test without login
        response_without_logging_in = self.client.post(
            reverse(ADD_SPOT_PATH_NAME) + '?lat=10.123&lon=20.456', post_data
        )
        self.assertEqual(response_without_logging_in.status_code, 404)

        # * Test with login but no lon and lat
        self.client.login(username=USERNAME, password=PASSWORD)
        with self.assertRaises(TypeError):
            response_no_lon_lat = self.client.post(
                reverse(ADD_SPOT_PATH_NAME)
            )
            self.assertEqual(response_no_lon_lat.context.get('error'), "We failed to obtain the longitude and latitude of the new spot you want to create. Please double check your URL to include valid longitude and latitude")
        
        # * Test with login and valid post_data
        response_with_valid_data = self.client.post(
                reverse(ADD_SPOT_PATH_NAME) + '?lat=10.123&lon=20.456', post_data
            )
        self.assertTrue(CreateParkingSpaceForm(data=post_data).is_valid())
        self.assertEqual(ParkingSpace.objects.count(), 1)
        saved_parking_spot = ParkingSpace.objects.first()
        self.assertEqual(saved_parking_spot.parking_spot_id, '1')
        self.assertEqual(saved_parking_spot.longitude, '20.456')
        self.assertEqual(saved_parking_spot.latitude, '10.123')
        self.assertEqual(saved_parking_spot.user.id, self.user.id)
        self.assertEqual(response_with_valid_data.status_code, 200)
        self.assertIsNotNone(response_with_valid_data.context.get('user_verification'))

        # * Test with login and INVALID post_data
        invalid_post_data = {"parking_spot_name": "TEST NAME"}
        response_with_invalid_data = self.client.post(
                reverse(ADD_SPOT_PATH_NAME) + '?lat=10.123&lon=20.456', invalid_post_data
            )
        self.assertFalse(CreateParkingSpaceForm(data=invalid_post_data).is_valid())
        self.assertIsNotNone(response_with_invalid_data.context.get('form'))
        

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
