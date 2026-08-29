from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self', 
        related_name='subcategories', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
        )
    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        if self.parent:
            return f'{self.name} under {self.parent.name}'
        return self.name

class City(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Ad(models.Model):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads')
    slug = models.SlugField(unique=True)    
    availability = models.BooleanField(default='is_available')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='ads/')
    location = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

class Conversation(models.Model):
    ad = models.ForeignKey(Ad, related_name='conversations', on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='buyer_conversations', on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='seller_conversations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name= 'unique_conversation_between_buyer_and_seller_per_ad',
                fields=['ad', 'buyer', 'seller'],
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'Conversation between {self.buyer} and {self.seller}'

class ReadStatus(models.TextChoices):
    READ = 'read'
    DELIVERED = 'delivered'
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name = 'messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender_messages', on_delete=models.CASCADE)
    text = models.TextField()
    read_status = models.CharField(
        max_length=10, 
        choices=ReadStatus.choices, 
        default=ReadStatus.DELIVERED
        )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender}`s messages'
    
class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saved_searches', on_delete=models.CASCADE)
    search_params = models.JSONField(default=dict)
    category = models.ForeignKey(Category, related_name='saved_searches', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Saved Searches'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_search_params_per_category',
                fields=['user', 'category']       
                  )
        ]
    def __str__(self):
        return f"{self.user}'s saved search at {self.created_at}"

class Review(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='buyer_reviews', on_delete=models.CASCADE)
    reviewed_seller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='seller_reviews', on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, related_name='reviews', on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                name='one_review_per_seller_on_one_ad',
                fields=['reviewer', 'reviewed_seller', 'ad']
            )
        ]

    def __str__(self):
        return f'{self.reviewer} rating on {self.ad}'

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    ad = models.ForeignKey(Ad, related_name='transactions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='one_transaction_amount_per_ad',
                fields=['user', 'amount', 'ad']
            )
        ]

    def __str__(self):
        return f'{self.user} transaction on {self.ad}'

