from rest_framework import serializers

from .models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class RestaurantIDSerializer(serializers.Serializer):
    """Validates input for a single restaurant ID"""
    restaurant_id = serializers.IntegerField()

    def validate_restaurant_id(self, value):
        if not Restaurant.objects.filter(id=value).exists():
            raise serializers.ValidationError("Restaurant with this ID does not exist.")
        return value
