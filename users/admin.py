"""user admin page registration
"""
from django.contrib import admin

from .models import User, UserVerification

# Register your models here.
admin.site.register(User)
admin.site.register(UserVerification)
