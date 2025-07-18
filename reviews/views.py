from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Review
from books.models import Book

@login_required
@require_POST
def rate_book(request):
    """Let users rate a book (AJAX)"""
    book_id = request.POST.get('book_id')
    rating = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '')
    
    # Check if rating is valid (1-5 stars)
    if not (1 <= rating <= 5):
        return JsonResponse({
            'success': False,
            'message': 'Rating must be between 1 and 5.'
        })
    
    try:
        # Get the book
        selected_book = Book.objects.get(id=book_id)
        
        # Check if user already reviewed this book
        existing_review, created = Review.objects.get_or_create(
            user=request.user,
            book=selected_book,
            defaults={'rating': rating, 'comment': comment}
        )
        
        if not created:
            # User already reviewed, update the review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
        
        # Update the book's average rating
        selected_book.update_average_rating()
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted successfully!',
            'average_rating': str(selected_book.average_rating),
            'total_ratings': selected_book.total_ratings
        })
    
    except Book.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Book not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error submitting rating.'
        })

@login_required
def my_reviews(request):
    """Show all reviews by the current user"""
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    # Split into pages
    from django.core.paginator import Paginator
    paginator = Paginator(user_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'reviews/my_reviews.html', context)

@login_required
def edit_review(request, review_id):
    """Let users edit their review"""
    # Get the review (only if it belongs to current user)
    user_review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        # User is updating their review
        new_rating = int(request.POST.get('rating', 0))
        new_comment = request.POST.get('comment', '')
        
        if 1 <= new_rating <= 5:
            user_review.rating = new_rating
            user_review.comment = new_comment
            user_review.save()
            
            # Update the book's average rating
            user_review.book.update_average_rating()
            
            messages.success(request, 'Review updated successfully!')
            return redirect('reviews:my_reviews')
        else:
            messages.error(request, 'Rating must be between 1 and 5.')
    
    context = {
        'review': user_review,
    }
    return render(request, 'reviews/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Let users delete their review"""
    # Get the review (only if it belongs to current user)
    user_review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        # Remember the book before deleting review
        book = user_review.book
        
        # Delete the review
        user_review.delete()
        
        # Update the book's average rating
        book.update_average_rating()
        
        messages.success(request, 'Review deleted successfully!')
        return redirect('reviews:my_reviews')
    
    context = {
        'review': user_review,
    }
    return render(request, 'reviews/delete_review.html', context)

def book_reviews(request, book_id):
    """Show all reviews for a specific book"""
    # Get the book
    selected_book = get_object_or_404(Book, id=book_id)
    
    # Get all reviews for this book
    book_reviews = Review.objects.filter(book=selected_book).order_by('-created_at')
    
    # Split into pages
    from django.core.paginator import Paginator
    paginator = Paginator(book_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if current user has reviewed this book
    user_review = None
    if request.user.is_authenticated:
        user_review = book_reviews.filter(user=request.user).first()
    
    context = {
        'book': selected_book,
        'page_obj': page_obj,
        'user_review': user_review,
    }
    return render(request, 'reviews/book_reviews.html', context)
