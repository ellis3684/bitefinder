import logging

from django.db import models

from restaurants.models import Restaurant


logger = logging.getLogger(__name__)


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    calories = models.IntegerField()
    fatsecret_food_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        unique_together = ("restaurant", "name")

    def __str__(self):
        return f"{self.name} ({self.calories} cal) - {self.restaurant.name}"

    @classmethod
    def update_menu_items(cls, restaurant, menu_items):
        """Update or create menu items for a given restaurant, storing FatSecret food ID."""
        logger.info(f"Updating menu items for {restaurant.name}")
        for item in menu_items:
            servings = item.get("servings", {}).get("serving", [])
            default_serving = next((s for s in servings if s.get("is_default") == "1"), servings[0] if servings else None)
            
            if default_serving:
                cls.objects.update_or_create(
                    restaurant=restaurant,
                    name=item["food_name"],
                    defaults={
                        "calories": int(float(default_serving["calories"])),
                        "fatsecret_food_id": item.get("food_id"),  # Nullable for API flexibility
                    },
                )
        logger.info(f"Finished updating menu items for {restaurant.name}")
