from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.models import Restaurant

from .meal_recommender import find_meal_combinations_efficient
from .models import MenuItem


class RecommendMealView(APIView):
    def get(self, request, restaurant_id, calorie_limit):
        """
        API endpoint to recommend a meal based on a restaurant's menu and calorie limit.
        
        :param restaurant_id: ID of the restaurant
        :param calorie_limit: Maximum calorie limit for the meal (must be > 0)
        :return: JSON response with recommended meal combinations
        """
        # Validate calorie limit
        if calorie_limit <= 0:
            return Response(
                {"error": "Calorie limit must be greater than 0"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        menu_items = MenuItem.objects.filter(restaurant=restaurant)

        if not menu_items.exists():
            return Response(
                {"error": "No menu items found for this restaurant."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        menu_data = [{
            "id": item.id,
            "name": item.name,
            "calories": item.calories
        } for item in menu_items]

        meal_combinations = find_meal_combinations_efficient(
            menu_data, 
            calorie_limit=calorie_limit
        )

        return Response({"recommended_meals": meal_combinations}, status=status.HTTP_200_OK)


class MenuItemListView(APIView):
    """
    API endpoint to get all menu items for a specific restaurant.
    """
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        menu_items = MenuItem.objects.filter(restaurant=restaurant).values('id', 'name', 'calories')
        return Response(menu_items, status=status.HTTP_200_OK)
