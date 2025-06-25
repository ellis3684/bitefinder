from django.urls import path

from .views import NearbyRestaurantsView, SupportedRestaurantsView

urlpatterns = [
    path("nearby/", NearbyRestaurantsView.as_view(), name="nearby_restaurants"),
    path("supported/", SupportedRestaurantsView.as_view(), name="supported_restaurants"),
]
