from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from books.models import Book

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.book.title} - {self.rating} stars'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the book's average rating
        self.book.update_average_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Update the book's average rating
        self.book.update_average_rating()
