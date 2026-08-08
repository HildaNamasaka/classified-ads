from rest_framework import serializers
from.models import User, Category, City,  Ad

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile_picture']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model=City
        fields = ['id','name']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class AdSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    location = CitySerializer(read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.all(),
        source = 'category',
        write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source = 'location',
        write_only = True
    )
    
    class Meta:
        model = Ad
        fields = '__all__'