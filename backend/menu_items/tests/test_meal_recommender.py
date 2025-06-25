from django.test import TestCase
from ..meal_recommender import find_meal_combinations_efficient, is_realistic_combination

class MealRecommenderTests(TestCase):
    def setUp(self):
        self.test_menu_items = [
            {"id": 1, "name": "Burger", "calories": 500},
            {"id": 2, "name": "Fries", "calories": 300},
            {"id": 3, "name": "Drink", "calories": 150},
            {"id": 4, "name": "Salad", "calories": 200},
            {"id": 5, "name": "Dessert", "calories": 400},
            {"id": 6, "name": "Small Fries", "calories": 200},
        ]

    def test_is_realistic_combination(self):
        """Test the heuristics for realistic meal combinations"""
        # Test too many of same item
        unrealistic_combo = [
            {"id": 1, "name": "Fries", "calories": 300},
            {"id": 2, "name": "Fries", "calories": 300},
            {"id": 3, "name": "Fries", "calories": 300},
        ]
        self.assertFalse(is_realistic_combination(unrealistic_combo))

        # Test calorie distribution (one item > 80% of total)
        unbalanced_combo = [
            {"id": 1, "name": "Burger", "calories": 800},
            {"id": 2, "name": "Small Side", "calories": 100},
        ]
        self.assertFalse(is_realistic_combination(unbalanced_combo))

        # Test minimum substance (no item > 150 calories)
        insubstantial_combo = [
            {"id": 1, "name": "Small Side 1", "calories": 100},
            {"id": 2, "name": "Small Side 2", "calories": 100},
        ]
        self.assertFalse(is_realistic_combination(insubstantial_combo))

        # Test valid combination
        valid_combo = [
            {"id": 1, "name": "Burger", "calories": 500},
            {"id": 2, "name": "Fries", "calories": 300},
            {"id": 3, "name": "Drink", "calories": 150},
        ]
        self.assertTrue(is_realistic_combination(valid_combo))

    def test_find_meal_combinations_efficient(self):
        """Test meal combination generation"""
        calorie_limit = 800
        combinations = find_meal_combinations_efficient(
            self.test_menu_items,
            calorie_limit=calorie_limit,
            target_count=5
        )

        # Check basic structure and constraints
        self.assertIsInstance(combinations, list)
        self.assertLessEqual(len(combinations), 5)
        
        for combo in combinations:
            # Check structure
            self.assertIn('items', combo)
            self.assertIsInstance(combo['items'], list)
            
            # Check calorie limit
            total_calories = sum(item['calories'] for item in combo['items'])
            self.assertLessEqual(total_calories, calorie_limit)
            
            # Check realistic combination
            self.assertTrue(is_realistic_combination(combo['items']))

    def test_empty_menu_items(self):
        """Test handling of empty menu items list"""
        combinations = find_meal_combinations_efficient([], calorie_limit=800)
        self.assertEqual(combinations, [])

    def test_impossible_calorie_limit(self):
        """Test handling of impossible calorie limit"""
        # Test with calorie limit lower than any item
        combinations = find_meal_combinations_efficient(
            self.test_menu_items,
            calorie_limit=100
        )
        self.assertEqual(combinations, []) 