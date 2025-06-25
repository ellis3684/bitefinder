from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from restaurants.models import Restaurant, DataSource

User = get_user_model()            # uses CustomUser

ME_FAV_URL = reverse("me-favorites")   # 'api/users/me/favorites/'

class FavoriteRestaurantTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create user + authenticate
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123!",
        )
        self.client.force_authenticate(self.user)

        # Restaurant fixture
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            data_source=DataSource.FATSECRET.value,
            is_active=True,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _payload(self, rest):
        """Helper returns JSON payload expected by POST/DELETE."""
        return {"restaurant_id": rest.id}

    # ------------------------------------------------------------------ #
    # Tests
    # ------------------------------------------------------------------ #
    def test_add_favorite(self):
        """POST should add a restaurant to the user’s favorites."""
        res = self.client.post(ME_FAV_URL, self._payload(self.restaurant))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(
            self.user.favorite_restaurants.filter(id=self.restaurant.id).exists()
        )

    def test_list_favorites(self):
        """GET returns the user’s favorite list."""
        self.user.favorite_restaurants.add(self.restaurant)

        res = self.client.get(ME_FAV_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data["favorite_restaurants"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test Restaurant")

    def test_remove_favorite(self):
        """DELETE should remove a favorite restaurant."""
        self.user.favorite_restaurants.add(self.restaurant)

        res = self.client.delete(ME_FAV_URL, self._payload(self.restaurant))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.user.favorite_restaurants.filter(id=self.restaurant.id).exists()
        )

    def test_idempotent_add(self):
        """
        Adding the same restaurant twice should not error
        and should not create duplicates.
        """
        self.user.favorite_restaurants.add(self.restaurant)

        res = self.client.post(ME_FAV_URL, self._payload(self.restaurant))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.favorite_restaurants.count(), 1)

    def test_add_nonexistent_restaurant(self):
        """Posting an invalid restaurant_id returns 400."""
        res = self.client.post(ME_FAV_URL, {"restaurant_id": 999})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
