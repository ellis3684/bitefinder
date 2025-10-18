import logging
import requests

from django.conf import settings
from rapidfuzz import process

from restaurants.models import Restaurant


logger = logging.getLogger(__name__)

class FoursquareAPI:
    BASE_URL = "https://places-api.foursquare.com/places/search"

    def __init__(self):
        self.api_key = settings.FOURSQUARE_API_KEY

    def fetch_chain_restaurants(self, lat, lng, chain_ids, radius=5000):
        """Fetch nearby restaurants that have a known Foursquare chain ID."""
        logger.info(f"Fetching chain restaurants for coordinates ({lat}, {lng})")
        
        all_results = []
        BATCH_SIZE = 100
        
        batches = [chain_ids[i:i+BATCH_SIZE] for i in range(0, len(chain_ids), BATCH_SIZE)]
        
        for batch in batches:
            params = {
                "ll": f"{lat},{lng}",
                "radius": radius,
                "limit": 50,
                "fields": "name,location,chains",
                "fsq_chain_ids": ",".join(batch)
            }
            headers = {"Authorization": self.api_key, "Accept": "application/json", "X-Places-Api-Version": "2025-06-17"}
            response = requests.get(self.BASE_URL, params=params, headers=headers)
            data = response.json()
            
            if "results" in data:
                for place in data["results"]:
                    formatted_address = place.get("location", {}).get("formatted_address", "Unknown Address")
                    chain_id = place.get("chains", [{}])[0].get("fsq_chain_id")
                    
                    try:
                        restaurant = Restaurant.objects.get(foursquare_chain_id=chain_id)
                        restaurant_id = restaurant.id
                        all_results.append({"id": restaurant_id, "name": place["name"], "formatted_address": formatted_address, "chain_id": chain_id})
                    except Restaurant.DoesNotExist:
                        logger.warning(f"Received unknown chain_id from Foursquare: {chain_id}, skipping restaurant: {place['name']}")
        
        return all_results

    def fetch_non_chain_restaurants(self, lat, lng, radius=5000, exclude_chain_ids=None):
        """Fetch nearby restaurants that do NOT have a Foursquare chain ID."""
        logger.info(f"Fetching non-chain restaurants for coordinates ({lat}, {lng})")
        
        all_results = []
        
        params = {"ll": f"{lat},{lng}", "radius": radius, "limit": 50, "fields": "name,location"}
        if exclude_chain_ids:
            params["exclude_chains"] = ",".join(exclude_chain_ids)
        headers = {"Authorization": self.api_key, "Accept": "application/json"}
        response = requests.get(self.BASE_URL, params=params, headers=headers)
        data = response.json()
        
        if "results" in data:
            restaurant_names = {restaurant.name.lower(): restaurant.id for restaurant in Restaurant.objects.filter(foursquare_chain_id__isnull=True)}
            
            for place in data["results"]:
                formatted_address = place.get("location", {}).get("formatted_address", "Unknown Address")
                match_result = process.extractOne(place["name"].lower(), restaurant_names.keys(), score_cutoff=90)
                
                if match_result:
                    restaurant_id = restaurant_names[match_result[0]]
                    all_results.append({"id": restaurant_id, "name": place["name"], "formatted_address": formatted_address})
                else:
                    logger.warning(f"No matching restaurant found for: {place['name']}, skipping.")
        
        return all_results

    def fetch_nearby_restaurants(self, lat, lng, chain_ids=None, radius=5000):
        """Fetch both chain and non-chain restaurants and merge results."""
        chain_results = self.fetch_chain_restaurants(lat, lng, chain_ids, radius) if chain_ids else []
        
        # Cap unique chain IDs at 100 from the chain results to avoid 414 URI too long
        exclude_chain_ids = list(set(r["chain_id"] for r in chain_results if r.get("chain_id")))[:100]
        
        non_chain_results = self.fetch_non_chain_restaurants(lat, lng, radius, exclude_chain_ids)

        return chain_results + non_chain_results
