from rest_framework import serializers
from.models import User, Category, City,  Ad, Conversation, Message, SavedSearch, Review, Transaction
import re
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile_picture']
        read_only_fields = ['date_joined']

class PublicSerializer(serializers.ModelSerializer):
    class Meta:
            model = User
            fields = ['id', 'username', 'profile_picture']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model=City
        fields = ['id','name']

class AdSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = PublicSerializer(read_only=True)
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

class AdPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fieds = ['id', 'title', 'price', 'photo']


class ConversationSerializer(serializers.ModelSerializer):
    ad = AdPreviewSerializer(read_only=True)
    buyer = PublicSerializer(read_only = True)
    seller = PublicSerializer(read_only = True)

    ad_id = serializers.PrimaryKeyRelatedField(
        queryset = Ad.objects.all(),
        source = 'ad',
        write_only = True
    )
    class Meta:
        model = Conversation
        fields = ['id', 'ad', 'buyer', 'seller', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = PublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'read_status', 'created_at']

class SavedSearchSerializer(serializers.ModelSerializer):
    user = PublicSerializer(read_only=True)

    class Meta:
        model = SavedSearch
        fields = ['id', 'user', 'search_params', 'category', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicSerializer(read_only=True)
    reviewed_seller = PublicSerializer(read_only=True)
    ad = AdPreviewSerializer(read_only=True)

    class Meta:
        model =Review
        fields = ['id', 'review', 'reviewed_seller', 'ad', 'rating', 'comment', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    user = PublicSerializer(read_only=True)
    ad = AdPreviewSerializer(read_only=True)

    def phone_number(self, value):
        pattern= r'^(254[71]\d{8}|0[71]\d{8})$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Enter a valid number')
        return value

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Amount cannot be less than 1')
        return value

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'ad', 'created_at']
        read_only_fields = ['checkout_request_id', 'mpesa_receipt_number', 'status', 'result_desc']

    

