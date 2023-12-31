import os

from django.core import mail
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from map.models import ParkingSpace
from map.scripts import load_parking_lot_data
from users.models import Post, Comment, UserWatchedParkingSpace


User = get_user_model()

TEST_LAT = 40.69446042799896
TEST_LON = -73.9864403526369
PARKINGSPACE_GET_API_PATH = "api:spots-near-center"

USERNAME = "parkrowd"
EMAIL = "parkrowd@gmail.com"
PASSWORD = "iLikeParking123!"
DUMMY_PASSWORD = "noParkingForYou"

PARKING_SPOT_ID = "12657"
FAKE_PARKING_SPOT_ID = "12677"
ADDRESS_ZIP = "10001"
LONGITUDE = "-73.9853043125"
LATITUDE = "40.7486538125"
PARKING_SPOT_NAME = "Empire State Building"
PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH = "api:change-occupancy"

PARKINGSPACE_POSTS_GET_PATH = "api:get-spot-posts"
TITLE = "Parking Here For 15 Minutes"
POST = "After 3:15, I'll be gone."
DATE = timezone.now()
COMMENT_CONTENT = "This is a comment"
PARKING_SPACE_COMMENT_POST_PATH = "api:add-comment"

EMAIL_HOST_USER = os.getenv("GOOGLE_SMTP_USERNAME")
PARKINGSPACE_ADD_WATCH_POST_PATH = "api:add-watch-on-spot"
PARKINGSPACE_REMOVE_WATCH_POST_PATH = "api:remove-watch-on-spot"


class ParkingSpaceNearCenterAPITest(APITestCase):
    """test getting parkingspaces near center GET"""

    def setUp(self):
        load_parking_lot_data.run()

    def test_get_parkingspaces(self):
        # * succeeded get
        response_success = self.client.get(
            reverse(PARKINGSPACE_GET_API_PATH) + f"?lat={TEST_LAT}&lon={TEST_LON}"
        )
        self.assertEqual(response_success.status_code, 200)
        self.assertTrue(len(response_success.data) > 0)

        # * failed get
        response_fail = self.client.get(reverse(PARKINGSPACE_GET_API_PATH))
        self.assertEqual(response_fail.status_code, 400)
        self.assertEqual(
            response_fail.data["message"], "Bad Request: Missing lat and lon parameters"
        )


class ParkingSpaceChangeOccupancyAPITest(APITestCase):
    """test change occupancy POST"""

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
        # * add a watch on the test spot, and see if occupancy change triggers email sending
        self.test_spot_watch = UserWatchedParkingSpace.objects.create(
            user=self.test_user, parking_space=self.test_spot
        )

    def test_change_occupancy(self):
        # * test non-logged-in post
        response_not_authorized = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 90},
        )
        self.assertEqual(response_not_authorized.status_code, 403)

        # * test logged-in post
        self.client.login(username=USERNAME, password=PASSWORD)

        response_authorized_missing_data = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH), {"percent": 90}
        )
        self.assertEqual(response_authorized_missing_data.status_code, 400)
        self.assertEqual(
            response_authorized_missing_data.data["message"],
            "Bad Request: Missing percent or id parameters",
        )

        response_authorized_with_wrong_data = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": FAKE_PARKING_SPOT_ID, "percent": 90},
        )
        self.assertEqual(response_authorized_with_wrong_data.status_code, 400)
        self.assertEqual(
            response_authorized_with_wrong_data.data["message"],
            "ParkingSpace with the specified id does not exist.",
        )

        # * Entering occupancy_percent as string based decimal
        response_authorized_with_string_based_decimal = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": "0.5"},
        )
        self.assertEqual(response_authorized_with_string_based_decimal.status_code, 400)
        self.assertEqual(
            response_authorized_with_string_based_decimal.data["message"],
            "Bad Request: Percent can only have digits",
        )

        # * Entering occupancy_percent with >100
        response_authorized_with_greater_than_100_occupancy = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 1234},
        )
        self.assertEqual(
            response_authorized_with_greater_than_100_occupancy.status_code, 400
        )
        self.assertEqual(
            response_authorized_with_greater_than_100_occupancy.data["message"],
            "Bad Request: Percent is >100",
        )

        # * Entering occupancy_percent as non-multiple of 10
        response_authorized_with_non_multiple_of_10 = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 5},
        )
        self.assertEqual(response_authorized_with_non_multiple_of_10.status_code, 400)
        self.assertEqual(
            response_authorized_with_non_multiple_of_10.data["message"],
            "Bad Request: Percent is not a multiple of 10",
        )

        # * test correct update
        response_authorized_with_correct_data = self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 90},
        )
        self.assertEqual(response_authorized_with_correct_data.status_code, 200)
        self.assertEqual(
            response_authorized_with_correct_data.data["message"],
            "Occupancy percent updated successfully.",
        )
        updatedParkingSpot = ParkingSpace.objects.get(parking_spot_id=PARKING_SPOT_ID)
        self.assertEqual(updatedParkingSpot.occupancy_percent, 90)

    def test_spot_watch(self):
        # * test logged-in post
        self.client.login(username=USERNAME, password=PASSWORD)
        # * change the occupancy to above threshold
        self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 100},
        )
        self.assertEqual(len(mail.outbox), 0)

        # * change the occupancy to below threshold
        self.client.post(
            reverse(PARKINGSPACE_CHANGE_OCCUPANCY_POST_PATH),
            {"id": PARKING_SPOT_ID, "percent": 50},
        )
        self.assertEqual(len(UserWatchedParkingSpace.objects.all()), 0)


class AddWatchOnParkingSpaceAPITest(APITestCase):
    """tests for adding watch on parking space's API"""

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

    def test_add_spot_watch(self):
        # * test non-logged-in post
        response_not_authorized = self.client.post(
            reverse(PARKINGSPACE_ADD_WATCH_POST_PATH),
            {"parking_spot_id": PARKING_SPOT_ID},
        )
        self.assertEqual(response_not_authorized.status_code, 403)

        # * test logged-in post
        self.client.login(username=USERNAME, password=PASSWORD)

        # * parking space does not exist
        response_parking_space_not_found = self.client.post(
            reverse(PARKINGSPACE_ADD_WATCH_POST_PATH),
            {"parking_spot_id": FAKE_PARKING_SPOT_ID},
        )
        self.assertEqual(response_parking_space_not_found.status_code, 400)

        # * success request
        response_success = self.client.post(
            reverse(PARKINGSPACE_ADD_WATCH_POST_PATH),
            {"parking_spot_id": PARKING_SPOT_ID},
        )
        self.assertEqual(response_success.status_code, 200)
        self.assertEqual(
            response_success.data,
            f"Watch on spot {self.test_spot.parking_spot_id} added",
        )
        self.assertEqual(
            len(UserWatchedParkingSpace.objects.filter(user=self.test_user)), 1
        )
        spot_watch_record = UserWatchedParkingSpace.objects.filter(user=self.test_user)[
            0
        ]
        self.assertEqual(spot_watch_record.user, self.test_user)
        self.assertEqual(spot_watch_record.parking_space, self.test_spot)


class RemoveWatchOnParkingSpaceAPITest(APITestCase):
    """tests for removing watch on parking space's API"""

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
        self.test_spot_watch = UserWatchedParkingSpace.objects.create(
            user=self.test_user, parking_space=self.test_spot
        )

    def test_add_spot_watch(self):
        # * make sure test_spot_watch created
        self.assertEqual(
            len(UserWatchedParkingSpace.objects.filter(user=self.test_user)), 1
        )

        # * test non-logged-in post
        response_not_authorized = self.client.post(
            reverse(PARKINGSPACE_REMOVE_WATCH_POST_PATH),
            {"parking_spot_id": PARKING_SPOT_ID},
        )
        self.assertEqual(response_not_authorized.status_code, 403)

        # * test logged-in post
        self.client.login(username=USERNAME, password=PASSWORD)
        # * parking space does not exist
        response_parking_space_not_found = self.client.post(
            reverse(PARKINGSPACE_REMOVE_WATCH_POST_PATH),
            {"parking_spot_id": FAKE_PARKING_SPOT_ID},
        )
        self.assertEqual(response_parking_space_not_found.status_code, 400)

        # * success request
        response_success = self.client.post(
            reverse(PARKINGSPACE_REMOVE_WATCH_POST_PATH),
            {"parking_spot_id": PARKING_SPOT_ID},
        )
        self.assertEqual(response_success.status_code, 200)
        self.assertEqual(
            response_success.data,
            f"Watch on spot {self.test_spot.parking_spot_id} removed",
        )
        self.assertEqual(
            len(UserWatchedParkingSpace.objects.filter(user=self.test_user)), 0
        )


class ParkingSpacePostsAndCommentsAPITest(APITestCase):
    """test getting posts under parking spot and
    test posting new comments
    """

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
        self.test_post = Post.objects.create(
            post=POST,
            title=TITLE,
            created_at=DATE,
            author=self.test_user,
            parking_space=self.test_spot,
        )
        self.test_comment = Comment.objects.create(
            content=COMMENT_CONTENT,
            author=self.test_user,
            post=self.test_post,
            created_at=DATE,
        )

    def test_get_posts(self):
        response = self.client.get(
            reverse(PARKINGSPACE_POSTS_GET_PATH, kwargs={"spotId": PARKING_SPOT_ID})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], TITLE)
        self.assertEqual(response.data[0]["post"], POST)
        self.assertEqual(len(response.data[0]["comments"]), 1)
        self.assertEqual(response.data[0]["comments"][0]["content"], COMMENT_CONTENT)

    def test_post_comment(self):
        # * test not-logged-in
        response_not_authorized = self.client.post(
            reverse(
                PARKING_SPACE_COMMENT_POST_PATH, kwargs={"postId": self.test_post.id}
            ),
            {"commentContent": COMMENT_CONTENT + "\nANOTHER TEST"},
        )
        self.assertEqual(response_not_authorized.status_code, 403)

        # * test logged-in
        self.client.login(username=USERNAME, password=PASSWORD)

        response_empty_content = self.client.post(
            reverse(
                PARKING_SPACE_COMMENT_POST_PATH, kwargs={"postId": self.test_post.id}
            ),
            {"commentContent": ""},
        )
        self.assertEqual(response_empty_content.status_code, 400)
        self.assertEqual(response_empty_content.data, "Error: empty comment content")

        fake_post_id = self.test_post.id + 100
        response_invalid_post_id = self.client.post(
            reverse(PARKING_SPACE_COMMENT_POST_PATH, kwargs={"postId": fake_post_id}),
            {"commentContent": COMMENT_CONTENT + "\nANOTHER TEST"},
        )
        self.assertEqual(response_invalid_post_id.status_code, 400)
        self.assertEqual(
            response_invalid_post_id.data, f"No post with post id {fake_post_id}"
        )

        response_success = self.client.post(
            reverse(
                PARKING_SPACE_COMMENT_POST_PATH, kwargs={"postId": self.test_post.id}
            ),
            {"commentContent": COMMENT_CONTENT + "\nANOTHER TEST"},
        )
        self.assertEqual(response_success.status_code, 200)
        self.assertEqual(
            response_success.data,
            "Comment created!",
        )
