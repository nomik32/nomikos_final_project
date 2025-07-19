from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

def register(request):
    """Let users create a new account"""
    if request.method == 'POST':
        # User submitted the registration form
        form = UserCreationForm(request.POST)
        
        # Get email from form
        email = request.POST.get('email', '').strip()
        
        # Check if email is provided
        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'accounts/register.html', {'form': form})
        
        # Check if email is already in use
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'accounts/register.html', {'form': form})
        
        if form.is_valid():
            try:
                # Create the new user
                new_user = form.save(commit=False)
                
                # Add email from the form
                new_user.email = email
                new_user.save()
                
                # Profile is automatically created by the signal in models.py
                
                # Log the user in automatically
                login(request, new_user)
                
                # Show success message
                messages.success(request, 'Account created successfully! Welcome to ReadEasy!')
                return redirect('home')
            except Exception as e:
                # If there's an error, delete the user and show error
                if new_user.id:
                    new_user.delete()
                messages.error(request, 'An error occurred while creating your account. Please try again.')
                return render(request, 'accounts/register.html', {'form': form})
    else:
        # Show the registration form
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """Show and edit user profile"""
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        # User is updating their profile
        user_profile.bio = request.POST.get('bio', '')
        user_profile.favorite_genre = request.POST.get('favorite_genre', '')
        user_profile.birth_date = request.POST.get('birth_date', '') or None
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    context = {
        'profile': user_profile,
    }
    return render(request, 'accounts/profile.html', context)




