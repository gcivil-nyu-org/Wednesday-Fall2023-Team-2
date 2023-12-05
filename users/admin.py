"""user admin page registration
"""
from django.contrib import admin

from .models import User, UserVerification, Post, Comment, UserWatchedParkingSpace

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserVerification)
admin.site.register(UserWatchedParkingSpace)
