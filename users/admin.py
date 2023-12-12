"""user admin page registration
"""
from django.contrib import admin

from .models import User, UserVerification, Post, Comment, UserWatchedParkingSpace


class UserAdmin(admin.ModelAdmin):
    """User Admin Page Manager"""

    search_fields = ["email", "username"]


class PostAdmin(admin.ModelAdmin):
    """Post Admin Page Manager"""

    search_fields = ["title", "post", "id"]
    autocomplete_fields = ["author", "parking_space"]


class CommentAdmin(admin.ModelAdmin):
    """Comment Admin Page Manager"""

    autocomplete_fields = ["author", "post"]


class UserVerificationAdmin(admin.ModelAdmin):
    """User Verification Admin Page Manager"""

    autocomplete_fields = ["username"]


class UserWatchedParkingSpaceAdmin(admin.ModelAdmin):
    """User Watched Parking Space Page Manager"""

    autocomplete_fields = ["user", "parking_space"]


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserVerification, UserVerificationAdmin)
admin.site.register(UserWatchedParkingSpace, UserWatchedParkingSpaceAdmin)
