import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.foursquare import FoursquareAPI

from .models import Restaurant


logger = logging.getLogger(__name__)


class NearbyRestaurantsView(APIView):
    """
    API endpoint to retrieve nearby restaurants based on latitude and longitude.

    - Fetches restaurants that have Foursquare chain IDs.
    - Fetches additional restaurants without chain IDs.
    - Logs important actions for debugging and monitoring.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("Received request for nearby restaurants with lat=%s, lng=%s", request.query_params.get("lat"), request.query_params.get("lng"))
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            logger.warning("Missing latitude or longitude in request")
            return Response({"error": "Latitude and longitude are required."}, status=400)
        
        lat, lng = float(lat), float(lng)
        cache_key = f"fsq:{round(lat, 3)}:{round(lng, 3)}"   # 110 m grid
        cached    = cache.get(cache_key)
        if cached:
            return Response(cached)          # ← no outbound API hit
        
        logger.info("Initializing FoursquareAPI")
        foursquare = FoursquareAPI()
        
        # Get all chain restaurant IDs
        logger.info("Fetching chain restaurant IDs from database")
        chain_restaurants = Restaurant.objects.exclude(foursquare_chain_id__isnull=True)
        chain_ids = list(chain_restaurants.values_list("foursquare_chain_id", flat=True))
        
        # Fetch restaurants using Foursquare API
        logger.info("Fetching restaurants from FoursquareAPI")
        all_results = foursquare.fetch_nearby_restaurants(lat, lng, chain_ids)
        logger.info("Successfully retrieved %d restaurants", len(all_results))
        
        cache.set(cache_key, all_results, 600)   # 600 s = 10 min

        return Response(all_results)

class SupportedRestaurantsView(APIView):
    """
    Return a list of all supported restaurants from the database.
    """

    def get(self, request):
        logger.info("Fetching all supported restaurants from the database.")
        restaurants = Restaurant.objects.all().values('id', 'name')
        return Response(restaurants, status=status.HTTP_200_OK)
