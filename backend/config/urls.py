from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/menu-items/', include('menu_items.urls')),
    path('api/restaurants/', include('restaurants.urls')),
    path("api/users/", include("users.urls")),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
