from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from restaurants.models import Restaurant, DataSource
from menu_items.models import MenuItem

class RecommendMealViewTests(APITestCase):
    def setUp(self):
        # Create test restaurant
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            data_source=DataSource.FATSECRET.value
        )

        # Create test menu items
        self.menu_items = [
            MenuItem.objects.create(
                restaurant=self.restaurant,
                name="Burger",
                calories=500
            ),
            MenuItem.objects.create(
                restaurant=self.restaurant,
                name="Fries",
                calories=300
            ),
            MenuItem.objects.create(
                restaurant=self.restaurant,
                name="Drink",
                calories=150
            ),
        ]

        self.url = reverse('recommend-meal', kwargs={
            'restaurant_id': self.restaurant.id,
            'calorie_limit': 800
        })

    def test_get_recommendations_success(self):
        """Test successful meal recommendations"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommended_meals', response.data)
        self.assertIsInstance(response.data['recommended_meals'], list)
        
        # Check first recommendation
        if response.data['recommended_meals']:
            first_meal = response.data['recommended_meals'][0]
            self.assertIn('items', first_meal)
            self.assertIsInstance(first_meal['items'], list)

    def test_restaurant_not_found(self):
        """Test handling of non-existent restaurant"""
        url = reverse('recommend-meal', kwargs={
            'restaurant_id': 99999,
            'calorie_limit': 800
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_menu(self):
        """Test handling of restaurant with no menu items"""
        empty_restaurant = Restaurant.objects.create(
            name="Empty Restaurant",
            data_source=DataSource.FATSECRET.value
        )
        url = reverse('recommend-meal', kwargs={
            'restaurant_id': empty_restaurant.id,
            'calorie_limit': 800
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_calorie_limit(self):
        """Test handling of invalid calorie limit"""
        # Test negative calorie limit - will not match URL pattern
        url = '/api/menu-items/recommend/{}/{}/'.format(
            self.restaurant.id, 
            -100
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test zero calorie limit - will match URL pattern but should be rejected by view
        url = reverse('recommend-meal', kwargs={
            'restaurant_id': self.restaurant.id,
            'calorie_limit': 0
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 