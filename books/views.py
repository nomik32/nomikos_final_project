from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Book, Category

def home(request):
    """This is the home page - shows featured books and latest books"""
    # Get books with high ratings for featured section
    featured_books = Book.objects.filter(average_rating__gte=4.0)[:6]
    
    # Get the newest books
    latest_books = Book.objects.all()[:8]
    
    # Get main categories
    categories = Category.objects.filter(parent=None)[:4]
    
    # Put everything in a dictionary to send to template
    context = {
        'featured_books': featured_books,
        'latest_books': latest_books,
        'categories': categories,
    }
    return render(request, 'books/home.html', context)

def book_list(request):
    """Show all books with search and filters"""
    # Start with all books
    books = Book.objects.all()
    
    # Check if user is searching
    search_query = request.GET.get('q')
    if search_query:
        # Search in title, author, and description
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Check if user selected a genre
    selected_genre = request.GET.get('genre')
    if selected_genre:
        books = books.filter(genre=selected_genre)
    
    # Check for price filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)
    
    # Check for year filter
    selected_year = request.GET.get('year')
    if selected_year:
        books = books.filter(publication_year=selected_year)
    
    # Sort the books
    sort_option = request.GET.get('sort', '-created_at')
    books = books.order_by(sort_option)
    
    # Split books into pages (12 per page)
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all genres and years for filter dropdowns
    all_genres = Book.objects.values_list('genre', flat=True).distinct()
    all_years = Book.objects.values_list('publication_year', flat=True).distinct().order_by('-publication_year')
    
    context = {
        'page_obj': page_obj,
        'genres': all_genres,
        'years': all_years,
        'current_filters': request.GET,
    }
    return render(request, 'books/book_list.html', context)

def book_detail(request, book_id):
    """Show details of one specific book"""
    # Get the book or show 404 error
    book = get_object_or_404(Book, id=book_id)
    
    # Find similar books (same category or genre)
    similar_books = Book.objects.filter(
        Q(category=book.category) | Q(genre=book.genre)
    ).exclude(id=book.id)[:4]
    
    # Check if user has already reviewed this book
    user_review = None
    if request.user.is_authenticated:
        user_review = book.reviews.filter(user=request.user).first()
    
    context = {
        'book': book,
        'related_books': similar_books,
        'user_review': user_review,
    }
    return render(request, 'books/book_detail.html', context)

def category_list(request):
    """Show all categories"""
    all_categories = Category.objects.all()
    context = {
        'categories': all_categories,
    }
    return render(request, 'books/category_list.html', context)

def category_detail(request, slug):
    """Show books in a specific category"""
    # Get the category or show 404
    category = get_object_or_404(Category, slug=slug)
    
    # Get all books in this category
    books_in_category = Book.objects.filter(category=category)
    
    # Check for search within category
    search_query = request.GET.get('q')
    if search_query:
        books_in_category = books_in_category.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Sort the books
    sort_option = request.GET.get('sort', '-created_at')
    books_in_category = books_in_category.order_by(sort_option)
    
    # Split into pages
    paginator = Paginator(books_in_category, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'books/category_detail.html', context)

def search(request):
    """Search books function"""
    search_query = request.GET.get('q', '')
    found_books = []
    
    if search_query:
        # Search in multiple fields
        found_books = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).order_by('-average_rating')
    
    # Split results into pages
    paginator = Paginator(found_books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': search_query,
        'page_obj': page_obj,
        'total_results': len(found_books),
    }
    return render(request, 'books/search_results.html', context)

@login_required
def book_preview(request, book_id):
    """Show book preview in a popup (AJAX)"""
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_preview.html', {'book': book})

def advanced_search(request):
    """Advanced search with many filters"""
    # Start with all books
    all_books = Book.objects.all()
    
    # Dictionary to store active filters
    active_filters = {}
    
    # Check each filter option
    if request.GET.get('title'):
        all_books = all_books.filter(title__icontains=request.GET['title'])
        active_filters['title'] = request.GET['title']
    
    if request.GET.get('author'):
        all_books = all_books.filter(author__icontains=request.GET['author'])
        active_filters['author'] = request.GET['author']
    
    if request.GET.get('genre'):
        all_books = all_books.filter(genre=request.GET['genre'])
        active_filters['genre'] = request.GET['genre']
    
    if request.GET.get('category'):
        all_books = all_books.filter(category__slug=request.GET['category'])
        active_filters['category'] = request.GET['category']
    
    if request.GET.get('min_price'):
        all_books = all_books.filter(price__gte=request.GET['min_price'])
        active_filters['min_price'] = request.GET['min_price']
    
    if request.GET.get('max_price'):
        all_books = all_books.filter(price__lte=request.GET['max_price'])
        active_filters['max_price'] = request.GET['max_price']
    
    if request.GET.get('min_year'):
        all_books = all_books.filter(publication_year__gte=request.GET['min_year'])
        active_filters['min_year'] = request.GET['min_year']
    
    if request.GET.get('max_year'):
        all_books = all_books.filter(publication_year__lte=request.GET['max_year'])
        active_filters['max_year'] = request.GET['max_year']
    
    # Sort the results
    sort_option = request.GET.get('sort', '-created_at')
    all_books = all_books.order_by(sort_option)
    
    # Split into pages
    paginator = Paginator(all_books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get options for filter dropdowns
    all_genres = Book.objects.values_list('genre', flat=True).distinct()
    all_categories = Category.objects.all()
    all_years = Book.objects.values_list('publication_year', flat=True).distinct().order_by('-publication_year')
    
    context = {
        'page_obj': page_obj,
        'filters': active_filters,
        'genres': all_genres,
        'categories': all_categories,
        'years': all_years,
    }
    return render(request, 'books/advanced_search.html', context)
