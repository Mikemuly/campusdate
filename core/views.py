"""
Views for CampusDate.

Each view handles one page/action:
  home            → landing page
  register        → user registration
  login_view      → login
  logout_view     → logout
  dashboard       → browse other students
  profile         → view any user's profile
  edit_profile    → edit own profile
  like_user       → like/unlike a user (AJAX-friendly)
  matches         → view all matches
  chat            → send/receive messages with a match
  search_users    → search users by name/campus
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import UserProfile, Campus, Like, Match, Message
from .forms import RegisterForm, ProfileEditForm, UserEditForm, MessageForm


# ──────────────────────────────────────────────
# Public pages
# ──────────────────────────────────────────────

def home(request):
    """Landing page — redirect logged-in users to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    stats = {
        'campus_count': Campus.objects.count(),
        'user_count': User.objects.filter(is_active=True).count(),
        'match_count': Match.objects.count(),
    }
    return render(request, 'core/home.html', stats)


def register(request):
    """Handle user registration form."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, f"Welcome to CampusDate, {user.first_name}! 🎉")
            return redirect('edit_profile')  # Prompt them to complete their profile
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'core/login.html')


@login_required
def logout_view(request):
    """Log the user out and redirect to home."""
    logout(request)
    messages.success(request, "You've been logged out. See you soon! 👋")
    return redirect('home')


# ──────────────────────────────────────────────
# Dashboard — browse users
# ──────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Main browsing page.
    Shows users from the same campus by default.
    Supports filtering by different campuses and name search.
    """
    try:
        current_profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('edit_profile')

    # Get filter params from URL query string
    campus_filter = request.GET.get('campus', '')
    name_search = request.GET.get('q', '').strip()
    show_all = request.GET.get('show_all', '')

    # Start with all users except self
    users_qs = User.objects.exclude(pk=request.user.pk).filter(
        is_active=True
    ).select_related('profile', 'profile__campus')

    # Require users to have a profile and a campus
    users_qs = users_qs.filter(profile__isnull=False, profile__campus__isnull=False)

    # Apply campus filter
    if campus_filter:
        users_qs = users_qs.filter(profile__campus_id=campus_filter)
    elif not show_all and current_profile.campus:
        # Default: same campus
        users_qs = users_qs.filter(profile__campus=current_profile.campus)

    # Apply name search
    if name_search:
        users_qs = users_qs.filter(
            Q(first_name__icontains=name_search) |
            Q(last_name__icontains=name_search) |
            Q(username__icontains=name_search)
        )

    # Get IDs of people already liked (to show liked state in UI)
    liked_ids = set(
        Like.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    )

    # Paginate — 12 users per page
    paginator = Paginator(users_qs, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    all_campuses = Campus.objects.all()

    context = {
        'page_obj': page_obj,
        'liked_ids': liked_ids,
        'all_campuses': all_campuses,
        'campus_filter': campus_filter,
        'name_search': name_search,
        'show_all': show_all,
        'current_campus': current_profile.campus,
    }
    return render(request, 'core/dashboard.html', context)


# ──────────────────────────────────────────────
# Profile pages
# ──────────────────────────────────────────────

@login_required
def profile(request, username=None):
    """
    View a user's profile.
    If no username given, show the logged-in user's own profile.
    """
    if username is None:
        target_user = request.user
    else:
        target_user = get_object_or_404(User, username=username, is_active=True)

    # Ensure profile exists
    profile_obj, _ = UserProfile.objects.get_or_create(user=target_user)

    is_own_profile = (target_user == request.user)
    has_liked = Like.objects.filter(from_user=request.user, to_user=target_user).exists()
    is_matched = Match.objects.filter(
        Q(user1=request.user, user2=target_user) |
        Q(user1=target_user, user2=request.user)
    ).first()

    context = {
        'target_user': target_user,
        'profile_obj': profile_obj,
        'is_own_profile': is_own_profile,
        'has_liked': has_liked,
        'match': is_matched,
    }
    return render(request, 'core/profile.html', context)


@login_required
def edit_profile(request):
    """Edit own profile: bio, picture, campus, interests, etc."""
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile_obj)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully! ✅")
            return redirect('profile_self')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile_obj)

    return render(request, 'core/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ──────────────────────────────────────────────
# Likes & Matches
# ──────────────────────────────────────────────

@login_required
def like_user(request, user_id):
    """
    Like or unlike a user.
    Accepts both POST form submissions and AJAX requests.
    Returns JSON for AJAX calls.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    target_user = get_object_or_404(User, pk=user_id, is_active=True)

    if target_user == request.user:
        return JsonResponse({'error': 'Cannot like yourself'}, status=400)

    # Toggle like
    like, created = Like.objects.get_or_create(
        from_user=request.user,
        to_user=target_user
    )

    if not created:
        # Already liked — remove the like (unlike)
        like.delete()
        liked = False
        is_match = False
    else:
        liked = True
        # Check if it created a match
        is_match = Match.objects.filter(
            Q(user1=request.user, user2=target_user) |
            Q(user1=target_user, user2=request.user)
        ).exists()

    # Return JSON for AJAX, redirect for form submissions
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'is_match': is_match,
            'match_message': f"🎉 It's a match with {target_user.first_name}!" if is_match else ''
        })

    if is_match:
        messages.success(request, f"🎉 You matched with {target_user.get_full_name()}!")
    elif liked:
        messages.info(request, f"You liked {target_user.first_name}!")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def matches(request):
    """Show all matches for the current user."""
    user_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related('user1__profile', 'user2__profile').order_by('-created_at')

    # Annotate each match with the other user and last message
    match_data = []
    for match in user_matches:
        other = match.get_other_user(request.user)
        last_msg = match.get_last_message()
        unread = match.get_unread_count(request.user)
        match_data.append({
            'match': match,
            'other_user': other,
            'last_message': last_msg,
            'unread_count': unread,
        })

    return render(request, 'core/matches.html', {'match_data': match_data})


# ──────────────────────────────────────────────
# Chat / Messaging
# ──────────────────────────────────────────────

@login_required
def chat(request, match_id):
    """
    Display conversation with a matched user.
    Only works if the two users are matched.
    """
    match = get_object_or_404(Match, pk=match_id)

    # Security: ensure current user is part of this match
    if request.user not in [match.user1, match.user2]:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('matches')

    other_user = match.get_other_user(request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                match=match,
                sender=request.user,
                content=form.cleaned_data['content']
            )
            # Mark received messages as read
            match.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
            return redirect('chat', match_id=match_id)
    else:
        form = MessageForm()
        # Mark messages as read when opening the chat
        match.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    chat_messages = match.messages.all().select_related('sender')

    return render(request, 'core/chat.html', {
        'match': match,
        'other_user': other_user,
        'chat_messages': chat_messages,
        'form': form,
    })


@login_required
def get_new_messages(request, match_id):
    """
    AJAX endpoint: return messages after a given message ID.
    Used for real-time-ish polling in the chat page.
    """
    match = get_object_or_404(Match, pk=match_id)
    if request.user not in [match.user1, match.user2]:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    after_id = request.GET.get('after', 0)
    new_msgs = match.messages.filter(pk__gt=after_id).select_related('sender')

    # Mark as read
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = [{
        'id': m.pk,
        'sender': m.sender.first_name or m.sender.username,
        'is_mine': m.sender == request.user,
        'content': m.content,
        'time': m.created_at.strftime('%H:%M'),
    } for m in new_msgs]

    return JsonResponse({'messages': data})
