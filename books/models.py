from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/category/{self.slug}/'

class Book(models.Model):
    GENRE_CHOICES = [
        ('romance', 'Romance'),
        ('mystery', 'Mystery'),
        ('sci-fi', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('self-help', 'Self-Help'),
        ('business', 'Business'),
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('study-guide', 'Study Guide'),
        ('children', 'Children\'s Books'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField()
    publication_year = models.IntegerField()
    publisher = models.CharField(max_length=200)
    page_count = models.PositiveIntegerField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/book/{self.id}/'

    def update_average_rating(self):
        """Update average rating based on reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(book=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg_rating, 2)
            self.total_ratings = reviews.count()
        else:
            self.average_rating = 0.00
            self.total_ratings = 0
        self.save()
