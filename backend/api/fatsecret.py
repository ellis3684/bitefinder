import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class FatSecretAPI:
    BASE_URL = "https://platform.fatsecret.com/rest/server.api"

    def __init__(self):
        self.client_id = settings.FATSECRET_CLIENT_ID
        self.client_secret = settings.FATSECRET_CLIENT_SECRET
        self.access_token = self.get_access_token()

    def get_access_token(self):
        """Authenticate with FatSecret and retrieve an access token."""
        logger.info("Fetching FatSecret access token")
        response = requests.post(
            "https://oauth.fatsecret.com/connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "premier"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response_data = response.json()
        if "access_token" not in response_data:
            logger.error("Failed to retrieve FatSecret access token: %s", response_data)
        return response_data.get("access_token")

    def get_restaurants(self):
        """Fetch restaurant brands from FatSecret."""
        logger.info("Fetching restaurant brands from FatSecret")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            self.BASE_URL,
            params={
                "method": "food_brands.get.v2",
                "format": "json",
                "brand_type": "restaurant"
            },
            headers=headers
        )
        data = response.json()
        if "food_brands" not in data:
            logger.warning("No restaurant brands found in FatSecret response: %s", data)
        return data.get("food_brands", {}).get("food_brand", [])

    def get_menu_items(self, restaurant_name, page=0):
        """Fetch menu items for a given restaurant using FatSecret v3 foods.search."""
        logger.info(f"Fetching menu items for {restaurant_name}, page {page}")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "include_sub_categories": True,
            "flag_default_serving": True,
            "method": "foods.search.v3",
            "search_expression": restaurant_name,
            "format": "json",
            "max_results": 50,
            "page_number": page
        }

        response = requests.get(self.BASE_URL, params=params, headers=headers)
        data = response.json()

        if not data or "foods_search" not in data or not data["foods_search"]:
            logger.warning(f"No menu items found for {restaurant_name} on page {page}")
            return []

        results = data["foods_search"].get("results")
        if results is None:
            logger.warning(f"Results key missing for {restaurant_name} on page {page}")
            return []

        menu_items = [
            item for item in results.get("food", [])
            if item.get("brand_name", "").lower() == restaurant_name.lower()
        ]

        if not menu_items:
            logger.info(f"No matching menu items found for {restaurant_name} on page {page}")
        return menu_items
