from unittest.mock import patch

from django.test import TestCase

from restaurants.models import DataSource
from restaurants.tasks import update_restaurants_task, prune_restaurants_task


class RestaurantTasksTest(TestCase):
    @patch("restaurants.tasks.FatSecretAPI.get_restaurants")
    @patch("restaurants.tasks.Restaurant.update_restaurants")
    def test_update_restaurants_task(self, mock_update_restaurants, mock_get_restaurants):
        """Ensure update_restaurants_task calls the API and updates restaurants."""
        mock_get_restaurants.return_value = ["McDonald's", "KFC"]
        
        result = update_restaurants_task()
        
        mock_get_restaurants.assert_called_once()
        mock_update_restaurants.assert_called_once_with(["McDonald's", "KFC"], source=DataSource.FATSECRET.value)
        self.assertEqual(result, "Updated 2 restaurants from FatSecret")

    @patch("restaurants.tasks.Restaurant.prune_inactive_restaurants")
    def test_prune_restaurants_task(self, mock_prune):
        """Ensure prune_restaurants_task removes old restaurants."""
        mock_prune.return_value = 5  # Simulate 5 restaurants being deleted

        result = prune_restaurants_task()

        mock_prune.assert_called_once()
        self.assertEqual(result, "Pruned 5 inactive restaurants past the retention period")
