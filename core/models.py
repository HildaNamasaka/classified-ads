from django.db import models
from django.contrib.auth.models import AbstractUser


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

    def __str__(self):
        return self.name

class Ad(models.Model):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    slug = models.SlugField(unique=True)    
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
