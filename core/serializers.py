from rest_framework import serializers
from.models import User, Category, City,  Ad, Conversation, Message, SavedSearch, Review, Transaction

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

class TransactionReview(serializers.ModelSerializer):
    user = PublicSerializer(read_only=True)
    ad = AdPreviewSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'ad', 'created_at']

