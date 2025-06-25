from django.test import TestCase
from django.utils.timezone import now, timedelta
import os
import tempfile
import pandas as pd
from restaurants.models import DataSource, Restaurant

class RestaurantModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.restaurant_1 = Restaurant.objects.create(name="McDonald's", data_source=DataSource.FATSECRET.value, is_active=True)
        self.restaurant_2 = Restaurant.objects.create(name="KFC", data_source=DataSource.FATSECRET.value, is_active=True)
        self.restaurant_3 = Restaurant.objects.create(name="Burger King", data_source=DataSource.FATSECRET.value, is_active=False, deactivated_at=now() - timedelta(days=100))
    
    def test_update_restaurants(self):
        """Ensure update_restaurants() adds, updates, and marks restaurants inactive."""
        new_brands = ["McDonald's", "KFC", "Subway"]

        Restaurant.update_restaurants(new_brands, source=DataSource.FATSECRET.value)

        self.assertTrue(Restaurant.objects.filter(name="Subway").exists())  # New restaurant added
        self.assertTrue(Restaurant.objects.get(name="Burger King").is_active is False)  # Inactive remains
        self.assertTrue(Restaurant.objects.get(name="KFC").is_active is True)  # Existing stays active

    def test_prune_inactive_restaurants(self):
        """Ensure prune_inactive_restaurants() removes old inactive restaurants."""
        Restaurant.prune_inactive_restaurants(retention_days=90)
        self.assertFalse(Restaurant.objects.filter(name="Burger King").exists())  # Should be deleted
    
    def test_update_chain_ids_from_file(self):
        """Test that the update_chain_ids_from_file method correctly updates chain IDs."""
        # Simulate a CSV file
        csv_data = pd.DataFrame({
            "chain_name": ["mcdonald's", "kfc"],
            "chain_id": ["12345", "67890"]
        })

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            csv_path = tmp_file.name
            csv_data.to_csv(csv_path, index=False)

        try:
            # Run method to update restaurants
            Restaurant.update_chain_ids_from_file(csv_path)

            # Fetch updated records
            self.restaurant_1.refresh_from_db()
            self.restaurant_2.refresh_from_db()
            self.restaurant_3.refresh_from_db()

            # Assertions
            self.assertEqual(self.restaurant_1.foursquare_chain_id, "12345")
            self.assertEqual(self.restaurant_2.foursquare_chain_id, "67890")
            self.assertIsNone(self.restaurant_3.foursquare_chain_id)  # Should remain unmatched
        
        finally:
            # Ensure file is deleted
            self.assertFalse(os.path.exists(csv_path))
