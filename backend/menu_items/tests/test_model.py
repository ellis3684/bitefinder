from django.test import TestCase
from menu_items.models import MenuItem
from restaurants.models import DataSource, Restaurant


class MenuItemModelTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", data_source=DataSource.FATSECRET.value)
        self.menu_items = [
            {
                "food_name": "Test Burger",
                "servings": {
                    "serving": [{"is_default": "1", "calories": "500"}]
                }
            },
            {
                "food_name": "Test Salad",
                "servings": {
                    "serving": [{"is_default": "1", "calories": "200"}]
                }
            }
        ]
    
    def test_update_menu_items_creates_items(self):
        """Test that menu items are correctly created."""
        MenuItem.update_menu_items(self.restaurant, self.menu_items)
        self.assertEqual(MenuItem.objects.count(), 2)
        self.assertTrue(MenuItem.objects.filter(name="Test Burger").exists())
        self.assertTrue(MenuItem.objects.filter(name="Test Salad").exists())

    def test_update_menu_items_updates_existing(self):
        """Test that updating menu items correctly updates existing entries."""
        MenuItem.objects.create(restaurant=self.restaurant, name="Test Burger", calories=300)
        MenuItem.update_menu_items(self.restaurant, self.menu_items)
        updated_item = MenuItem.objects.get(name="Test Burger")
        self.assertEqual(updated_item.calories, 500)

    def test_update_menu_items_handles_no_servings(self):
        """Test that menu items without servings are ignored."""
        invalid_items = [{"food_name": "No Serving Item", "servings": {"serving": []}}]
        MenuItem.update_menu_items(self.restaurant, invalid_items)
        self.assertFalse(MenuItem.objects.filter(name="No Serving Item").exists()) 