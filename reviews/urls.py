from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('rate/', views.rate_book, name='rate_book'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('book/<int:book_id>/', views.book_reviews, name='book_reviews'),
] 