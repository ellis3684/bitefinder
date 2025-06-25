from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from restaurants.models import Restaurant, DataSource

NEARBY_URL_NAME = "nearby_restaurants"
PATCH_PATH = "api.foursquare.FoursquareAPI.fetch_nearby_restaurants"


class TestRestaurantsView(APITestCase):
    def setUp(self):
        self.url = reverse(NEARBY_URL_NAME)

        # At least one chain record so the view passes chain_ids
        Restaurant.objects.create(
            name="UnitTest Eatery",
            data_source=DataSource.FATSECRET.value,
            is_active=True,
            foursquare_chain_id="fsq123",
        )

    @patch(PATCH_PATH)
    def test_nearby_restaurants_success(self, mock_fetch):
        """Endpoint returns the list provided by FoursquareAPI."""
        dummy_payload = [
            {"id": 1, "name": "Foo", "formatted_address": "123 St"},
            {"id": 2, "name": "Bar", "formatted_address": "456 Ave"},
        ]
        mock_fetch.return_value = dummy_payload

        resp = self.client.get(self.url, {"lat": 41.0, "lng": -71.0})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), len(dummy_payload))

        chain_ids = list(
            Restaurant.objects.exclude(
                foursquare_chain_id__isnull=True
            ).values_list("foursquare_chain_id", flat=True)
        )
        mock_fetch.assert_called_once_with(41.0, -71.0, chain_ids)

    def test_missing_query_params(self):
        """lat & lng are required."""
        resp = self.client.get(self.url)  # no params
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
