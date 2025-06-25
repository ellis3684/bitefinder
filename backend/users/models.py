from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    favorite_restaurants = models.ManyToManyField("restaurants.Restaurant")


class UserMeal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meals")
    restaurant = models.ForeignKey("restaurants.Restaurant", on_delete=models.CASCADE)
    menu_items = models.ManyToManyField("menu_items.MenuItem", related_name="meals")
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_calories(self):
        """Return the total calories for this meal."""
        return sum(item.calories for item in self.menu_items.all())
