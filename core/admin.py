"""
Django admin registration for CampusDate models.
Access at /admin/ after creating a superuser.
"""

from django.contrib import admin
from .models import Campus, UserProfile, Like, Match, Message


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'campus', 'age', 'gender', 'created_at']
    list_filter = ['campus', 'gender']
    search_fields = ['user__username', 'user__email', 'bio']
    raw_id_fields = ['user', 'campus']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'created_at']
    list_filter = ['created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at']
    list_filter = ['created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'match', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username']
