from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib import messages
from .forms import SignUpForm, UpdateProfileForm, ContactForm
from django.contrib.auth.models import User
from .models import UserProfile


def login_user(request):
    """User login authentication view."""
    if request.method == 'POST':
        username_or_email = request.POST["username_or_email"]
        password = request.POST["password"]

        # Check if the input contains '@' to determine whether it's an email or
        # username.
        if "@" in username_or_email:
            # Try to get a user with the provided email.
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_or_email,
                                password=password)

        if user is not None:
            login(request, user)
            # Redirect to a home page.
            messages.success(request, (
                'You are logged in. Congrats!'), extra_tags='success')
            return redirect('/')
        else:
            # Return an 'invalid login' error message.
            messages.error(request, (
                'Login error! Please check your username and password.'),
                extra_tags='danger')
            return redirect('login')
    else:
        return render(request, 'authentication/login.html', {})


def logout_user(request):
    """User logout view."""
    logout(request)
    messages.success(request, ('You have been logged out!', ),
                     extra_tags='info')
    return redirect('/')


def register_user(request):
    """User registration view."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('You have registered!'),
                             extra_tags='success')
            return redirect('/')
        else:
            messages.error(request, ('Registration error!'),
                           extra_tags='danger')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'authentication/signup.html', context)


@login_required
def user_profile(request):
    """User profile view."""
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'user_profile.html', context)


@login_required
def update_profile(request):
    """Update Profile View."""
    # Get the user's profile instance
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If the user's profile doesn't exist, create a new one
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES,
                                 instance=request.user)

        if form.is_valid():
            # Use commit=False to prevent saving the User model for now
            user = form.save(commit=False)

            # Check if the user entered a new password
            new_password = form.cleaned_data.get('new_password1')
            new_password_confirm = form.cleaned_data.get('new_password2')

            if new_password != new_password_confirm:
                form.add_error('new_password1',
                               'The two password fields didn\'t match.')
                return render(request, 'user_profile_update.html',
                              {'form': form}
                              )

            if new_password:
                # Validate the new password
                try:
                    validate_password(new_password)
                except ValidationError as errors:
                    for error in errors.error_list:
                        form.add_error('new_password1', error)
                    return render(request, 'user_profile_update.html',
                                  {'form': form})

                # Update the user's password and keep them logged in
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)

            # Check if the user is changing the email address
            new_email = form.cleaned_data.get('email')
            if new_email and new_email != user.email:
                email_validator = EmailValidator(
                    message='Enter a valid email address.')

                try:
                    email_validator(new_email)
                except ValidationError:
                    form.add_error('email', 'Invalid email format.')
                    return render(request, 'user_profile_update.html',
                                  {'form': form})

                # Check if the new email address is unique
                if User.objects.filter(email=new_email
                                       ).exclude(
                                           username=user.username).exists():
                    form.add_error('email',
                                   'This email address is already in use.')
                    return render(request, 'user_profile_update.html',
                                  {'form': form})

                # Update the email address
                user.email = new_email

            # Check if the user is updating the profile image
            if form.cleaned_data.get('profile_image'):
                # Update the profile image
                user_profile.profile_image = form.cleaned_data['profile_image']

            user.save()  # Save the updated User model
            user_profile.save()  # Save the updated UserProfile model

            messages.success(request, (
                'Your profile was successfully updated!'),
                extra_tags='success')
            return redirect('user_profile')

    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'user_profile_update.html', {'form': form})


@login_required
def delete_profile(request):
    """Delete user profile view."""
    if request.method == 'POST':
        # delete user  and log out
        request.user.delete()
        return redirect('home')  # after deletion redirect to home page

    return render(request, 'profile.html', {'user': request.user})


def contact(request):
    """Contact form view."""
    initial_data = {}

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # If authenticated, populate the initial_data dictionary with user's
        # name and email
        name = request.user.first_name
        initial_data['name'] = name if name else request.user.username
        initial_data['email'] = request.user.email

    form = ContactForm(initial=initial_data)
    return render(request, 'contact.html', {'form': form})


def custom_404_view(request, exception):
    """Custom 404 error view."""
    return render(request, '404.html', {}, status=404)
