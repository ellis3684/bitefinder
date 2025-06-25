from django.urls import path
from .views import RecommendMealView, MenuItemListView

urlpatterns = [
    path('recommend/<int:restaurant_id>/<int:calorie_limit>/', RecommendMealView.as_view(), name='recommend-meal'),
    path('restaurant/<int:restaurant_id>/', MenuItemListView.as_view(), name='menu-items-list'),
]
