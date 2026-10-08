from django.urls import path
from .views import (UserCreate, UserDetail, CategoryList, CategoryDetail, 
                    CityList, CityDetail, AdList, AdDetail, ConversationList, 
                    MessageList, MessageDetail, SavedSearchList, SavedSearchDetail, 
                    ReviewList, ReviewDetail,  TransactionList, MpesaCallback)

urlpatterns=[
    path('users/', UserCreate.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('categories/', CategoryList.as_view()),
    path('categories/<slug:slug>/', CategoryDetail.as_view()),
    path('ads/', AdList.as_view()),
    path('ad/<slug:slug>/',AdDetail.as_view()),
    path('reviews/', ReviewList.as_view()),
    path('reviews/<int:pk>/', ReviewDetail.as_view()),
    path('cities/', CityList.as_view()),
    path('cities/<slug:slug>/', CityDetail.as_view()),    
    path('conversations/', ConversationList.as_view()),
    path('conversations/<int:conversation_pk>/messages/', MessageList.as_view()),
    path('conversations/<int:conversation_pk>/messages/<int:pk>/', MessageDetail.as_view()),
    path('saved-searches/', SavedSearchList.as_view()),
    path('saved-searches/<int:pk>/', SavedSearchDetail.as_view()),    
    path('transactions/', TransactionList.as_view()),
    path('mpesa/callback/', MpesaCallback.as_view()),
]