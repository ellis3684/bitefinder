import unittest
from unittest.mock import patch, MagicMock
from api.foursquare import FoursquareAPI

class TestFoursquareAPI(unittest.TestCase):

    @patch("api.foursquare.Restaurant.objects.get")
    @patch("api.foursquare.requests.get")
    def test_fetch_chain_restaurants(self, mock_requests_get, mock_restaurant_get):
        # Create a dummy restaurant to return from the ORM call
        dummy_restaurant = MagicMock()
        dummy_restaurant.id = 1
        mock_restaurant_get.return_value = dummy_restaurant

        # Mock the Foursquare API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Burger King",
                    "location": {"formatted_address": "123 Main St"},
                    "chains": [{"id": "burger_king"}]
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        api = FoursquareAPI()
        response = api.fetch_chain_restaurants(41.0, -71.0, ["burger_king"])
        
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["name"], "Burger King")
        self.assertEqual(response[0]["formatted_address"], "123 Main St")
        self.assertEqual(response[0]["chain_id"], "burger_king")
        mock_requests_get.assert_called_once()
    
    @patch("api.foursquare.Restaurant.objects.filter")
    @patch("api.foursquare.requests.get")
    def test_fetch_non_chain_restaurants(self, mock_requests_get, mock_restaurant_filter):
        # Create a dummy restaurant for the filter call
        dummy_restaurant = MagicMock()
        dummy_restaurant.id = 2
        dummy_restaurant.name = "Local Diner"
        mock_restaurant_filter.return_value = [dummy_restaurant]

        # Mock the Foursquare API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Local Diner",
                    "location": {"formatted_address": "456 Elm St"}
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        api = FoursquareAPI()
        response = api.fetch_non_chain_restaurants(41.0, -71.0)
        
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["name"], "Local Diner")
        self.assertEqual(response[0]["formatted_address"], "456 Elm St")
        mock_requests_get.assert_called_once()
    
    @patch("api.foursquare.Restaurant.objects.filter")
    @patch("api.foursquare.Restaurant.objects.get")
    @patch("api.foursquare.requests.get")
    def test_fetch_nearby_restaurants(self, mock_requests_get, mock_restaurant_get, mock_restaurant_filter):
        # Dummy for chain fetch
        dummy_restaurant_chain = MagicMock()
        dummy_restaurant_chain.id = 3
        mock_restaurant_get.r
