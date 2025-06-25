import logging

from django.contrib.auth import get_user_model, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from restaurants.models import Restaurant
from restaurants.serializers import RestaurantIDSerializer

from .models import UserMeal
from .serializers import (
    FavoriteRestaurantInfoSerializer,
    UserMealSerializer,
    UserCreateSerializer,
    UserInfoSerializer,
    LoginSerializer
)


logger = logging.getLogger(__name__)
User = get_user_model()


@ensure_csrf_cookie
@api_view(["GET"])
def csrf_view(request):
    return Response({"detail": "CSRF cookie set"})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        return Response(UserInfoSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class MeInfoView(generics.RetrieveAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class MeFavoriteRestaurantsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = FavoriteRestaurantInfoSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = RestaurantIDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        restaurant = Restaurant.objects.get(id=serializer.validated_data["restaurant_id"])
        request.user.favorite_restaurants.add(restaurant)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        serializer = RestaurantIDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        restaurant = Restaurant.objects.get(id=serializer.validated_data["restaurant_id"])
        request.user.favorite_restaurants.remove(restaurant)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeMealsView(ModelViewSet):
    serializer_class = UserMealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMeal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
