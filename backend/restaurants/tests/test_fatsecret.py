import unittest
from unittest.mock import patch

from api.fatsecret import FatSecretAPI


class TestFatSecretAPI(unittest.TestCase):
    @patch("api.fatsecret.requests.post")
    def test_get_access_token(self, mock_post):
        """Ensure the API retrieves an access token successfully."""
        mock_post.return_value.json.return_value = {"access_token": "test_token"}
        
        api = FatSecretAPI()
        self.assertEqual(api.access_token, "test_token")

    @patch("api.fatsecret.requests.get")
    def test_get_restaurants(self, mock_get):
        """Ensure get_restaurants() correctly fetches data."""
        mock_get.return_value.json.return_value = {
            "food_brands": {"food_brand": ["McDonald's", "KFC", "Burger King"]}
        }

        api = FatSecretAPI()
        restaurants = api.get_restaurants()
        self.assertEqual(restaurants, ["McDonald's", "KFC", "Burger King"])

    @patch("api.fatsecret.requests.get")
    def test_get_restaurants_handles_failure(self, mock_get):
        """Ensure get_restaurants() handles API failures."""
        mock_get.return_value.json.return_value = {}
        
        api = FatSecretAPI()
        restaurants = api.get_restaurants()
        self.assertEqual(restaurants, [])  # Should return an empty list on failure
