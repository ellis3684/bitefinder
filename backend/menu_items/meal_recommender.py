import random
from itertools import combinations
from typing import List, Dict, TypedDict, Union, Any

class MenuItem(TypedDict):
    id: Union[int, str]  # Could be either int or str depending on source
    name: str
    calories: int

class MealCombination(TypedDict):
    items: List[MenuItem]

def is_realistic_combination(items: List[MenuItem]) -> bool:
    """Apply heuristics to determine if this is a realistic meal combination."""
    # Check 1: Not too many of the same item
    item_counts: Dict[str, int] = {}
    for item in items:
        name = item['name']
        item_counts[name] = item_counts.get(name, 0) + 1
        if item_counts[name] > 2:  # Allow at most 2 of any item
            return False
    
    # Check 2: Calorie distribution is reasonable
    calories = [item['calories'] for item in items]
    if max(calories) > sum(calories) * 0.8:  # One item shouldn't be > 80% of calories
        return False
    
    # Check 3: Ensure meal has some substance
    if max(calories) < 150:  # At least one substantial item
        return False
    
    return True

def find_meal_combinations_efficient(
    menu_items: List[MenuItem],
    calorie_limit: int,
    target_count: int = 20,
    min_efficiency: float = 0.7,
    max_items: int = 4
) -> List[MealCombination]:
    """
    Find valid meal combinations within calorie limit with improved efficiency.
    
    Args:
        menu_items: List of dicts containing menu items with 'id', 'name', and 'calories'
        calorie_limit: Maximum calories allowed for the meal
        target_count: Number of meal combinations to return
        min_efficiency: Minimum ratio of total calories to calorie limit
        max_items: Maximum number of items in a combination
    
    Returns:
        List of dicts containing just the menu items in each combination
    """
    # Early return for empty menu items
    if not menu_items:
        return []

    valid_meals: List[Dict] = []  # Using Dict temporarily for internal processing
    
    # First try smaller combinations which are less computationally expensive
    for num_items in range(1, min(3, max_items) + 1):
        for combo in combinations(menu_items, num_items):
            total_calories = sum(item['calories'] for item in combo)
            
            if total_calories <= calorie_limit and total_calories >= calorie_limit * min_efficiency:
                efficiency = total_calories / calorie_limit
                
                if is_realistic_combination(list(combo)):
                    valid_meals.append({
                        'items': list(combo),
                        'total_calories': total_calories,
                        'efficiency': efficiency,
                        'item_count': len(combo)
                    })
                    
                    if len(valid_meals) >= target_count * 3:
                        break
        
        if len(valid_meals) >= target_count * 3:
            break
    
    # If we don't have enough combinations yet, try larger combinations with sampling
    if len(valid_meals) < target_count and max_items > 2:
        filtered_items = [item for item in menu_items if item['calories'] <= calorie_limit * 0.8]
        
        if filtered_items:  # Only proceed if we have items to work with
            attempts = 0
            max_attempts = 10000
            
            while len(valid_meals) < target_count * 3 and attempts < max_attempts:
                attempts += 1
                
                # Generate weights matching the actual range size
                size_range = list(range(3, max_items + 1))
                weights = [5] * len(size_range)  # Equal weights for simplicity
                
                # Randomly select number of items
                num_items = min(random.choices(size_range, weights=weights)[0], len(filtered_items))
                
                # Randomly select items
                combo = random.sample(filtered_items, num_items)
                total_calories = sum(item['calories'] for item in combo)
                
                if total_calories <= calorie_limit and total_calories >= calorie_limit * min_efficiency:
                    efficiency = total_calories / calorie_limit
                    
                    if is_realistic_combination(combo):
                        is_unique = True
                        for meal in valid_meals[-10:]:
                            if set(item['id'] for item in combo) == set(item['id'] for item in meal['items']):
                                is_unique = False
                                break
                        
                        if is_unique:
                            valid_meals.append({
                                'items': combo,
                                'total_calories': total_calories,
                                'efficiency': efficiency,
                                'item_count': len(combo)
                            })
    
    # Sort by efficiency and extract just the items
    valid_meals.sort(key=lambda x: (x['efficiency'], -x['item_count']), reverse=True)
    
    # Return only the items for each meal combination
    return [{'items': meal['items']} for meal in valid_meals[:target_count]]
