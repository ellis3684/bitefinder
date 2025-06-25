import logging

from celery import shared_task

from api.fatsecret import FatSecretAPI

from .models import DataSource, Restaurant

logger = logging.getLogger(__name__)

@shared_task
def update_restaurants_task():
    """
    Celery task to update restaurant data from FatSecret.
    """
    logger.info("update_restaurants_task started")
    try:
        fatsecret = FatSecretAPI()
        brand_list = fatsecret.get_restaurants()
        if not brand_list:
            logger.warning("No restaurants found in FatSecret response.")
        
        Restaurant.update_restaurants(brand_list, source=DataSource.FATSECRET.value)
        logger.info(f"Successfully updated {len(brand_list)} restaurants from FatSecret.")
        return f"Updated {len(brand_list)} restaurants from FatSecret"
    except Exception as e:
        logger.exception("Error updating restaurants from FatSecret")
        raise e

@shared_task
def prune_restaurants_task():
    """
    Celery task to remove restaurants that have been inactive for 90+ days.
    """
    logger.info("prune_restaurants_task started")
    try:
        count_removed = Restaurant.prune_inactive_restaurants()
        logger.info(f"Pruned {count_removed} inactive restaurants past the retention period.")
        return f"Pruned {count_removed} inactive restaurants past the retention period"
    except Exception as e:
        logger.exception("Error pruning inactive restaurants")
        raise e
