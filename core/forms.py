"""
Forms for CampusDate.

Covers registration, login, profile editing.
All inputs are validated server-side by Django forms.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Campus


class RegisterForm(UserCreationForm):
    """
    Extended registration form.
    Adds: first_name, last_name, email, age, gender, campus.
    Inherits password hashing from UserCreationForm.
    """
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'your@university.edu', 'class': 'form-input'})
    )
    age = forms.IntegerField(
        min_value=17,
        max_value=35,
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Your Age', 'class': 'form-input'})
    )
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    campus = forms.ModelChoiceField(
        queryset=Campus.objects.all(),
        required=True,
        empty_label="— Select Your Campus —",
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'age', 'gender', 'campus', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the default fields from UserCreationForm
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username', 'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password (min 8 chars)', 'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-input'})

    def clean_email(self):
        """Ensure email is unique across all users."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        """Save user and automatically create their UserProfile."""
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create the linked UserProfile
            UserProfile.objects.create(
                user=user,
                age=self.cleaned_data['age'],
                gender=self.cleaned_data['gender'],
                campus=self.cleaned_data['campus'],
            )
        return user


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing UserProfile fields.
    Handles bio, campus, age, gender, interests, profile picture.
    """
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'age', 'gender', 'campus', 'interests']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a short bio about yourself...',
                'class': 'form-input',
                'maxlength': 500
            }),
            'age': forms.NumberInput(attrs={'class': 'form-input', 'min': 17, 'max': 35}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'campus': forms.Select(attrs={'class': 'form-input'}),
            'interests': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. hiking, music, coding, photography'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }

    def clean_profile_picture(self):
        """Validate file size (max 5MB) and type."""
        picture = self.cleaned_data.get('profile_picture')
        if picture and hasattr(picture, 'size'):
            if picture.size > 5 * 1024 * 1024:  # 5 MB limit
                raise forms.ValidationError("Image must be under 5MB.")
            # Check content type
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(picture, 'content_type') and picture.content_type not in valid_types:
                raise forms.ValidationError("Only JPEG, PNG, GIF, WEBP images are accepted.")
        return picture


class UserEditForm(forms.ModelForm):
    """Form for editing the base User fields (name, email)."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        """Ensure email uniqueness (excluding the current user)."""
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class MessageForm(forms.Form):
    """Simple form for sending a chat message."""
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': 'Type a message...',
            'class': 'message-input',
            'id': 'messageInput'
        })
    )
