from django.test import TestCase


# class CreatePostTests(TestCase):
#     def test_post_view(self):
#         """checks if post page returns a 200 status code
#         and the template 'map/post.html' is used
#         """
#         response = self.client.get(reverse(POST_PATH_NAME))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, POST_TEMPLATE)

#     def test_successful_post(self):
#         """checks if post is made successfully
#         and redirects (Status 302) to Map Page
#         """
#         post_data = {
#             "author": AUTHOR,
#             "title": TITLE,
#             "post": POST,
#             "created_at": DATE,
#             "spot": SPOT,
#         }
#         response = self.client.post(reverse(POST_PATH_NAME), user_data)
#         self.assertRedirects(response, reverse(MAP_PATH_NAME))
#         self.assertTrue(User.objects.filter(username=USERNAME).exists())
