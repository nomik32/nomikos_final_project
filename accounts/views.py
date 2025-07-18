from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg
from .models import UserProfile
from books.models import Book
from reviews.models import Review
from cart.models import Cart

def register(request):
    """Let users create a new account"""
    if request.method == 'POST':
        # User submitted the registration form
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create the new user
            new_user = form.save()
            
            # Create a profile for the new user
            UserProfile.objects.create(user=new_user)
            
            # Log the user in automatically
            login(request, new_user)
            
            # Show success message
            messages.success(request, 'Account created successfully! Welcome to ReadEasy!')
            return redirect('home')
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

@login_required
def dashboard(request):
    """Show user's dashboard with their activity"""
    current_user = request.user
    
    # Get user's recent reviews
    recent_reviews = Review.objects.filter(user=current_user).order_by('-created_at')[:5]
    
    # Get books the user has reviewed recently
    recent_books = Book.objects.filter(reviews__user=current_user).distinct().order_by('-reviews__created_at')[:5]
    
    # Get user's shopping cart
    user_cart, created = Cart.objects.get_or_create(user=current_user)
    
    # Calculate user statistics
    total_reviews = Review.objects.filter(user=current_user).count()
    total_books_reviewed = Book.objects.filter(reviews__user=current_user).distinct().count()
    average_rating = Review.objects.filter(user=current_user).aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
    
    # Find user's favorite genres
    favorite_genres = Review.objects.filter(user=current_user).values('book__genre').annotate(
        count=Count('book__genre')
    ).order_by('-count')[:3]
    
    context = {
        'recent_reviews': recent_reviews,
        'recent_books': recent_books,
        'cart': user_cart,
        'total_reviews': total_reviews,
        'total_books_reviewed': total_books_reviewed,
        'average_rating': round(average_rating, 1),
        'favorite_genres': favorite_genres,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def reading_history(request):
    """Show all books the user has reviewed"""
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    # Split into pages
    from django.core.paginator import Paginator
    paginator = Paginator(user_reviews, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'accounts/reading_history.html', context)

@login_required
def wishlist(request):
    """Show user's wishlist (books rated 4+ stars)"""
    # For now, we use books rated 4+ stars as wishlist
    wishlist_books = Book.objects.filter(
        reviews__user=request.user,
        reviews__rating__gte=4
    ).distinct()
    
    context = {
        'wishlist_books': wishlist_books,
    }
    return render(request, 'accounts/wishlist.html', context)

@login_required
@require_POST
def toggle_wishlist(request):
    """Add or remove book from wishlist (AJAX)"""
    book_id = request.POST.get('book_id')
    selected_book = get_object_or_404(Book, id=book_id)
    
    # Check if book is already in wishlist (rated 4+ stars)
    existing_review = Review.objects.filter(user=request.user, book=selected_book).first()
    
    if existing_review and existing_review.rating >= 4:
        # Remove from wishlist by lowering rating
        existing_review.rating = 3
        existing_review.save()
        in_wishlist = False
        message = 'Book removed from wishlist.'
    else:
        # Add to wishlist by rating 4+ stars
        if existing_review:
            existing_review.rating = 4
            existing_review.save()
        else:
            Review.objects.create(user=request.user, book=selected_book, rating=4)
        in_wishlist = True
        message = 'Book added to wishlist.'
    
    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
        'message': message
    })

@login_required
def settings(request):
    """Let users change their account settings"""
    if request.method == 'POST':
        # Update user information
        current_user = request.user
        current_user.first_name = request.POST.get('first_name', '')
        current_user.last_name = request.POST.get('last_name', '')
        current_user.email = request.POST.get('email', '')
        current_user.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('accounts:settings')
    
    return render(request, 'accounts/settings.html')
