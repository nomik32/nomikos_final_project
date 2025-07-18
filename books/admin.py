from django.contrib import admin
from .models import Category, Book

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'category', 'price', 'average_rating', 'publication_year']
    list_filter = ['genre', 'category', 'publication_year', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'description']
    list_editable = ['price']
    readonly_fields = ['average_rating', 'total_ratings']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'genre', 'category')
        }),
        ('Details', {
            'fields': ('description', 'publication_year', 'publisher', 'page_count')
        }),
        ('Pricing & Media', {
            'fields': ('price', 'cover_image')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_ratings'),
            'classes': ('collapse',)
        }),
    )
