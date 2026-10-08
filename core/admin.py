from django.contrib import admin

from .models import User, Category,  Ad, Conversation, Message, SavedSearch, Review, Transaction

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Ad)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(SavedSearch)
admin.site.register(Review)
admin.site.register(Transaction)