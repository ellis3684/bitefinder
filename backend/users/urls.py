from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    csrf_view, MeFavoriteRestaurantsView, MeInfoView,
    UserCreateView, MeMealsView, LoginView, LogoutView
)


me_router = DefaultRouter()
me_router.register(r'meals', MeMealsView, basename='me-meals')

urlpatterns = [
    path('csrf/', csrf_view),

    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # For general user functionality (not scoped to "me")
    path('create/', UserCreateView.as_view(), name='user-create'),

    # For user-specific functionality (scoped to "me")
    path('me/', MeInfoView.as_view(), name='me-info'),
    path('me/favorites/', MeFavoriteRestaurantsView.as_view(), name='me-favorites'),
    path('me/', include(me_router.urls)),
]
