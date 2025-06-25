import logging
from celery import shared_task
from api.fatsecret import FatSecretAPI
from menu_items.models import MenuItem
from restaurants.models import Restaurant

logger = logging.getLogger("celery")

@shared_task
def update_menu_items_task():
    """Fetch and store menu items for all restaurants in the database."""
    logger.info("update_menu_items_task started")
    try:
        fatsecret = FatSecretAPI()
        for restaurant in Restaurant.objects.all():
            page = 0
            while True:
                menu_items = fatsecret.get_menu_items(restaurant.name, page=page)
                if not menu_items:
                    break  # No more pages
                
                MenuItem.update_menu_items(restaurant, menu_items)
                page += 1  # Go to next page

        logger.info("Successfully updated menu items for all restaurants.")
        return "Updated menu items for all restaurants."
    except Exception as e:
        logger.exception("Error updating menu items.")
        raise e
