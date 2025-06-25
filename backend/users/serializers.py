import logging

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

from menu_items.serializers import MenuItemSerializer
from menu_items.models import MenuItem
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer

from .models import UserMeal


logger = logging.getLogger(__name__)
User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        return data


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class FavoriteRestaurantInfoSerializer(serializers.ModelSerializer):
    """Lightweight serializer for a user's favorite restaurants"""
    favorite_restaurants = RestaurantSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('favorite_restaurants',)


class UserMealSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    menu_item_ids = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        many=True,
        source="menu_items",
        write_only=True
    )

    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(),
        source="restaurant",
        write_only=True
    )

    def update(self, instance, validated_data):
        new_menu_item_ids = validated_data.get("menu_item_ids")
        if new_menu_item_ids is not None:
            instance.menu_items.set(new_menu_item_ids)
        return instance
    
    class Meta:
        model = UserMeal
        fields = (
            "id",
            "restaurant",
            "restaurant_id",
            "menu_items",
            "menu_item_ids",
            "created_at",
        )
        read_only_fields = ('id', 'created_at')
