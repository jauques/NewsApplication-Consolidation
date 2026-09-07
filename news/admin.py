"""
Admin configuration for the News Application.

This module registers the application's models so they can be managed
through the Django administration site.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomUser,
    Publisher,
    Article,
    Newsletter
)

# Register the custom user model using Django's built-in UserAdmin.
admin.site.register(CustomUser, UserAdmin)

# Register publisher records for management in Django Admin.
admin.site.register(Publisher)

# Register articles created by journalists.
admin.site.register(Article)

# Register newsletters and their linked articles.
admin.site.register(Newsletter)
