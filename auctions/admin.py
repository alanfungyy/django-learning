from django.contrib import admin
from .models import User, Listing, Bid, Comment

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "price", "category", "active")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "user", "price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "listing", "user")

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
