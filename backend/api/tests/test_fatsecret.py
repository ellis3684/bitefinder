import unittest
from unittest.mock import patch, MagicMock
from api.fatsecret import FatSecretAPI

class TestFatSecretAPI(unittest.TestCase):
    
    @patch("api.fatsecret.requests.post")
    def test_get_access_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value = mock_response
        
        api = FatSecretAPI()
        self.assertEqual(api.access_token, "mock_token")
        mock_post.assert_called_once()
    
    @patch("api.fatsecret.requests.get")
    def test_get_restaurants(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"food_brands": {"food_brand": [{"brand_id": "456", "brand_name": "Subway"}]}}
        mock_get.return_value = mock_response
        
        api = FatSecretAPI()
        api.access_token = "mock_token"
        response = api.get_restaurants()
        
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["brand_name"], "Subway")
        mock_get.assert_called_once()

@patch("api.fatsecret.requests.get")
def test_get_menu_items(self, mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "foods_search": {
            "results": {
                "food": [
                    {
                        "food_id": "123",
                        "food_name": "Big Mac",
                        "brand_name": "McDonald's"
                    }
                ]
            }
        }
    }
    mock_get.return_value = mock_response
    
    api = FatSecretAPI()
    api.access_token = "mock_token"
    response = api.get_menu_items("McDonald's")
    
    self.assertEqual(len(response), 1)
    self.assertEqual(response[0]["food_id"], "123")
    self.assertEqual(response[0]["food_name"], "Big Mac")
    self.assertEqual(response[0]["brand_name"], "McDonald's")
    mock_get.assert_called_once()
