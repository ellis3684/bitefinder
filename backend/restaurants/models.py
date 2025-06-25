from datetime import timedelta
from enum import Enum
import logging
import os
import pandas as pd

from django.db import models
from django.utils.timezone import now
from rapidfuzz import process


logger = logging.getLogger(__name__)

class DataSource(Enum):
    """
    Enum to track the data source of restaurant records.
    Currently, only FatSecret is used.
    "OTHER" is a placeholder in case additional providers are added later.
    """
    FATSECRET = "fatsecret"
    OTHER = "other"

class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    data_source = models.CharField(max_length=50, choices=[(tag.value, tag.name) for tag in DataSource])  # API source
    is_active = models.BooleanField(default=True)  # Track whether a brand is still active
    deactivated_at = models.DateTimeField(null=True, blank=True)  # Timestamp when it was marked inactive
    foursquare_chain_id = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Foursquare chain ID

    def __str__(self):
        return self.name

    @classmethod
    def update_restaurants(cls, brand_list, source):
        """
        Update or create restaurant records and mark those no longer in the latest dataset as inactive.
        """
        logger.info("Updating restaurant records from source: %s", source)
        current_brand_names = set(brand_list)

        for brand_name in brand_list:
            cls.objects.update_or_create(
                name=brand_name,
                data_source=source,
                defaults={"is_active": True, "deactivated_at": None},
            )

        # Mark removed restaurants as inactive instead of deleting them
        inactive_count = cls.objects.filter(is_active=True, data_source=source).exclude(name__in=current_brand_names).update(
            is_active=False, deactivated_at=now()
        )
        logger.info("Marked %d restaurants as inactive.", inactive_count)
    
    @classmethod
    def prune_inactive_restaurants(cls, retention_days=90):
        """
        Permanently delete restaurants that have been inactive for more than retention_days.
        """
        logger.info("Pruning inactive restaurants older than %d days.", retention_days)
        threshold_date = now() - timedelta(days=retention_days)
        deleted_count, _ = cls.objects.filter(is_active=False, deactivated_at__lte=threshold_date).delete()
        logger.info("Deleted %d inactive restaurants.", deleted_count)
    
    @classmethod
    def update_chain_ids_from_file(cls, csv_path):
        """Process a manually downloaded Foursquare chain CSV and update the database."""
        if not os.path.exists(csv_path):
            logger.error(f"Provided CSV file does not exist: {csv_path}")
            return "CSV file not found"

        logger.info(f"Processing Foursquare chain CSV from: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            df["chain_name"] = df["chain_name"].str.lower()

            restaurants = list(cls.objects.values_list("name", flat=True))
            restaurants_lower = {name.lower(): name for name in restaurants}

            matched = {}
            unmatched_db_restaurants = set(restaurants_lower.values())

            for _, row in df.iterrows():
                chain_name = row["chain_name"]
                chain_id = row["chain_id"]

                if chain_name in restaurants_lower:
                    matched[restaurants_lower[chain_name]] = chain_id
                    unmatched_db_restaurants.discard(restaurants_lower[chain_name])
                else:
                    match_result = process.extractOne(chain_name, restaurants_lower.keys(), score_cutoff=90)
                    if match_result:
                        best_match, _, _ = match_result
                        db_restaurant = restaurants_lower[best_match]
                        if db_restaurant not in matched:
                            matched[db_restaurant] = chain_id
                            unmatched_db_restaurants.discard(db_restaurant)

            for name, chain_id in matched.items():
                cls.objects.filter(name=name).update(foursquare_chain_id=chain_id)

            logger.info(f"Updated {len(matched)} restaurants with Foursquare chain IDs.")
            logger.info(f"{len(unmatched_db_restaurants)} restaurants remain unmatched.")
            return f"Updated {len(matched)} restaurants, {len(unmatched_db_restaurants)} unmatched."

        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return "Error processing CSV"

        finally:
            os.remove(csv_path)
            logger.info(f"Deleted processed CSV file: {csv_path}")
