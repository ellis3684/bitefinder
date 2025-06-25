from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from restaurants.models import Restaurant, DataSource
from menu_items.models import MenuItem
from users.models import UserMeal   # adjust import path if different

User = get_user_model()

MEALS_URL = reverse("me-meals-list")
def meal_detail_url(meal_id):
    return reverse("me-meals-detail", args=[meal_id])


class UserMealTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # User ↔ auth
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123!",
        )
        self.client.force_authenticate(self.user)

        # Restaurant + menu items
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            data_source=DataSource.FATSECRET.value,
            is_active=True,
        )
        self.menu_item1 = MenuItem.objects.create(
            name="Item 1",
            calories=500,
            restaurant=self.restaurant,
        )
        self.menu_item2 = MenuItem.objects.create(
            name="Item 2",
            calories=300,
            restaurant=self.restaurant,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _payload(self, items):
        """Return POST/PUT payload matching serializer."""
        return {
            "restaurant_id": self.restaurant.id,
            "menu_item_ids": [obj.id for obj in items],
        }

    # ------------------------------------------------------------------ #
    # Tests
    # ------------------------------------------------------------------ #
    def test_create_meal(self):
        """POST should create a meal with menu items."""
        res = self.client.post(
            MEALS_URL,
            self._payload([self.menu_item1, self.menu_item2]),
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        meal = UserMeal.objects.get(id=res.data["id"])
        self.assertEqual(meal.menu_items.count(), 2)
        self.assertEqual(meal.total_calories, 800)  # 500 + 300

    def test_list_meals(self):
        """GET returns user’s meals."""
        meal = UserMeal.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )
        meal.menu_items.add(self.menu_item1)

        res = self.client.get(MEALS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["menu_items"][0]["name"], "Item 1")

    def test_get_meal_detail(self):
        """Detail view returns full meal info."""
        meal = UserMeal.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )
        meal.menu_items.add(self.menu_item1, self.menu_item2)

        url = meal_detail_url(meal.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["menu_items"]), 2)

        # DB-derived calories (not in response payload)
        meal.refresh_from_db()
        self.assertEqual(meal.total_calories, 800)

    def test_delete_meal(self):
        """DELETE removes the meal."""
        meal = UserMeal.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )
        url = meal_detail_url(meal.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserMeal.objects.filter(id=meal.id).exists())

    def test_invalid_menu_item(self):
        """Posting a non-existent menu_item_id returns 400."""
        res = self.client.post(
            MEALS_URL,
            {"restaurant_id": self.restaurant.id, "menu_item_ids": [999]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
