"""
Models for CampusDate.

Tables:
  - Campus       : universities/colleges on the platform
  - UserProfile  : extends Django's built-in User with extra fields
  - Like         : one user liking another
  - Match        : created when two users mutually like each other
  - Message      : chat messages between matched users
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Campus(models.Model):
    """Represents a university or college."""
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200, blank=True)  # City/Country
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Campuses'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Extends Django's User model with dating-profile fields.
    One-to-one relationship: each User has exactly one UserProfile.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('O', 'Other'),
        ('PNS', 'Prefer not to say'),
    ]

    # Link to Django's built-in User (handles auth, password hashing, etc.)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Personal info
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell others about yourself (max 500 chars)")

    # Profile picture — stored in media/profile_pics/
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        default=None
    )

    # Campus association — required for filtering
    campus = models.ForeignKey(
        Campus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    # Interests / hobbies (free text, comma-separated)
    interests = models.CharField(max_length=300, blank=True, help_text="e.g. hiking, music, coding")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"

    def get_profile_picture_url(self):
        """Return profile picture URL or a default placeholder."""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/core/img/default_avatar.svg'

    def has_liked(self, other_user):
        """Check if this user's account has liked the given user."""
        return Like.objects.filter(from_user=self.user, to_user=other_user).exists()

    def is_matched_with(self, other_user):
        """Check if this user is matched with another user."""
        return Match.objects.filter(
            models.Q(user1=self.user, user2=other_user) |
            models.Q(user1=other_user, user2=self.user)
        ).exists()


class Like(models.Model):
    """
    Records that from_user liked to_user.
    After saving, we check if to_user also liked from_user → create Match.
    """
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Can only like once
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} ❤ {self.to_user.username}"

    def save(self, *args, **kwargs):
        """Override save to auto-create a Match if mutual like exists."""
        super().save(*args, **kwargs)
        # Check if the other person already liked us back
        mutual = Like.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).exists()
        if mutual:
            # Create match (avoid duplicates with get_or_create)
            # Always store with lower user_id first for consistency
            user1, user2 = sorted([self.from_user, self.to_user], key=lambda u: u.id)
            Match.objects.get_or_create(user1=user1, user2=user2)


class Match(models.Model):
    """
    A mutual match between two users.
    Only matched users can message each other.
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-created_at']

    def __str__(self):
        return f"Match: {self.user1.username} ↔ {self.user2.username}"

    def get_other_user(self, current_user):
        """Given one user in the match, return the other."""
        return self.user2 if self.user1 == current_user else self.user1

    def get_last_message(self):
        """Return the most recent message in this match's conversation."""
        return self.messages.order_by('-created_at').first()

    def get_unread_count(self, user):
        """Count unread messages for a specific user."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    A chat message between two matched users.
    Messages are tied to a Match, not directly to users, for clarity.
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=1000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
