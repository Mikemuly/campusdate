"""
URL patterns for the CampusDate core app.

Maps URLs to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Public pages ──────────────────────────────
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard (browse users) ───────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Profile pages ──────────────────────────────
    path('profile/', views.profile, name='profile_self'),          # Own profile
    path('profile/<str:username>/', views.profile, name='profile'),  # Any user's profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # ── Likes & Matching ───────────────────────────
    path('like/<int:user_id>/', views.like_user, name='like_user'),
    path('matches/', views.matches, name='matches'),

    # ── Chat / Messaging ───────────────────────────
    path('chat/<int:match_id>/', views.chat, name='chat'),
    path('chat/<int:match_id>/messages/', views.get_new_messages, name='get_new_messages'),
]
