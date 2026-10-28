from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from .serializers import UserSerializer, CategorySerializer, CitySerializer, AdSerializer, ConversationSerializer, MessageSerializer, SavedSearchSerializer, ReviewSerializer, TransactionSerializer
from .models import User, Category, City, Ad, Conversation, Message, SavedSearch, Review, Transaction
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly, IsParticipant, CanEditWithinWindow, IsOwner
from django.db.models import Q
from .mpesa import stk_push
from .tasks import addition

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from.models import Transaction, TransactionStatus
from rest_framework.permissions import AllowAny
from django.db import transaction as db_transaction

class UserCreate(generics.CreateAPIView):
    serializer_class= UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = 'slug'
    
class CityList(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

class CityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsStaffOrReadOnly]
    lookup_field = 'slug'

class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller = self.request.user) 

class AdDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'slug'

class ConversationList(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(buyer=user) | Q(seller=user))

    def perform_create(self, serializer):
        ad = serializer.validated_data['ad']
        conversation, created = Conversation.objects.get_or_create(
            ad = ad,
            buyer = self.request.user,
            seller = ad.seller
        )

        serializer.instance = conversation

class MessageList(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['conversation_pk'])
        self.check_object_permissions(self.request, conversation)
        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, pk=self.kwargs['conversation_pk'])
        self.check_object_permissions(self.request, conversation)
        serializer.save(sender=self.request.user, conversation=conversation, read_status = 'delivered')

class MessageDetail(generics.RetrieveUpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditWithinWindow]

    def get_queryset(self):
        return Message.objects.filter(conversation_id = self.kwargs['conversation_pk'])

class SavedSearchList(generics.ListCreateAPIView):
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user_id = self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavedSearchDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavedSearchSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

class ReviewList(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.all()
        ad_id = self.request.query_params.get('ad')
        seller_id= self.request.query_params.get('seller')

        if ad_id is not None:
            queryset = queryset.filter(ad=ad_id)
        if seller_id is not None:
            queryset = queryset.filter(reviewed_seller = seller_id)
        return queryset

    def perform_create(self, serializer):
        ad = serializer.validated_data['ad']
        serializer.save(reviewer = self.request.user, reviewed_seller=ad.seller)

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class TransactionList(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']
        phone_number=serializer.validated_data['phone_number']
        

        result = stk_push(
            amount=amount,
            phone_number=phone_number,
                     
        )
        print(result)
        checkout_request_id = result.get('CheckoutRequestID')
        
        if checkout_request_id is None:
            raise serializers.ValidationError("Could not initiate M-Pesa payment. Please try again.")
            
        
        serializer.save(user=self.request.user, checkout_request_id=checkout_request_id)  

class MpesaCallback(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        callback_data = request.data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = callback_data.get('CheckoutRequestID')
        result_code = callback_data.get('ResultCode')
        result_desc = callback_data.get('ResultDesc')

        with db_transaction.atomic():
            transaction_obj = Transaction.objects.select_for_update().filter(checkout_request_id=checkout_request_id).first()

            if transaction_obj is None:
                return Response({'ResultCode' : 0, 'ResultDesc' : 'The service request is processed successfully'}, status=status.HTTP_200_OK)

            if result_code == 0 and not transaction_obj.mpesa_receipt_number:
                metadata = callback_data.get('CallbackMetadata', {}).get('Item', [])
                values = {item['Name'] : item.get('Value') for item in metadata}

                transaction_obj.mpesa_receipt_number = values.get('MpesaReceiptNumber')
                transaction_obj.apply_result(result_code, result_desc)
                transaction_obj.save()

            else:
                transaction_obj.apply_result(result_code, result_desc)
                return Response({'ResultCode' : 0, 'ResultDesc' : 'The service request is processed successfully'}, status=status.HTTP_200_OK)
        return Response({'ResultCode' : 0, 'ResultDesc' : 'The service request is processed successfully'}, status=status.HTTP_200_OK)
        
    