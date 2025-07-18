from django.core.management.base import BaseCommand
from books.models import Category, Book
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate the database with sample books and categories'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Fiction',
                'description': 'Imaginative literature including novels, short stories, and poetry.',
                'slug': 'fiction'
            },
            {
                'name': 'Non-Fiction',
                'description': 'Factual literature including biographies, history, and self-help.',
                'slug': 'non-fiction'
            },
            {
                'name': 'Educational',
                'description': 'Academic and educational materials including textbooks and reference books.',
                'slug': 'educational'
            },
            {
                'name': 'Children\'s Books',
                'description': 'Books specifically written for children and young readers.',
                'slug': 'children'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create sample books
        books_data = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'genre': 'romance',
                'category': categories['fiction'],
                'price': 12.99,
                'description': 'A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.',
                'publication_year': 1925,
                'publisher': 'Scribner',
                'page_count': 180
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780446310789',
                'genre': 'mystery',
                'category': categories['fiction'],
                'price': 14.99,
                'description': 'The story of young Scout Finch and her father Atticus in a racially divided Alabama town.',
                'publication_year': 1960,
                'publisher': 'Grand Central Publishing',
                'page_count': 281
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'genre': 'sci-fi',
                'category': categories['fiction'],
                'price': 11.99,
                'description': 'A dystopian novel about totalitarianism and surveillance society.',
                'publication_year': 1949,
                'publisher': 'Signet Classic',
                'page_count': 328
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780547928241',
                'genre': 'fantasy',
                'category': categories['fiction'],
                'price': 15.99,
                'description': 'The adventure of Bilbo Baggins, a hobbit who embarks on a quest with thirteen dwarves.',
                'publication_year': 1937,
                'publisher': 'Houghton Mifflin',
                'page_count': 366
            },
            {
                'title': 'Steve Jobs',
                'author': 'Walter Isaacson',
                'isbn': '9781451648539',
                'genre': 'biography',
                'category': categories['non-fiction'],
                'price': 18.99,
                'description': 'The biography of Apple co-founder Steve Jobs, based on interviews with Jobs and others.',
                'publication_year': 2011,
                'publisher': 'Simon & Schuster',
                'page_count': 656
            },
            {
                'title': 'Sapiens: A Brief History of Humankind',
                'author': 'Yuval Noah Harari',
                'isbn': '9780062316097',
                'genre': 'history',
                'category': categories['non-fiction'],
                'price': 16.99,
                'description': 'A groundbreaking narrative of humanity\'s creation and evolution.',
                'publication_year': 2015,
                'publisher': 'Harper',
                'page_count': 443
            },
            {
                'title': 'The 7 Habits of Highly Effective People',
                'author': 'Stephen R. Covey',
                'isbn': '9780743269513',
                'genre': 'self-help',
                'category': categories['non-fiction'],
                'price': 13.99,
                'description': 'A self-help book presenting an approach to being effective in attaining goals.',
                'publication_year': 1989,
                'publisher': 'Free Press',
                'page_count': 381
            },
            {
                'title': 'The Lean Startup',
                'author': 'Eric Ries',
                'isbn': '9780307887894',
                'genre': 'business',
                'category': categories['non-fiction'],
                'price': 17.99,
                'description': 'How today\'s entrepreneurs use continuous innovation to create radically successful businesses.',
                'publication_year': 2011,
                'publisher': 'Crown Business',
                'page_count': 336
            },
            {
                'title': 'Introduction to Python Programming',
                'author': 'Dr. John Smith',
                'isbn': '9781234567890',
                'genre': 'textbook',
                'category': categories['educational'],
                'price': 29.99,
                'description': 'A comprehensive guide to Python programming for beginners.',
                'publication_year': 2023,
                'publisher': 'Tech Books Inc.',
                'page_count': 450
            },
            {
                'title': 'Advanced Mathematics',
                'author': 'Dr. Sarah Johnson',
                'isbn': '9780987654321',
                'genre': 'reference',
                'category': categories['educational'],
                'price': 34.99,
                'description': 'Advanced mathematical concepts and problem-solving techniques.',
                'publication_year': 2022,
                'publisher': 'Academic Press',
                'page_count': 520
            },
            {
                'title': 'The Little Prince',
                'author': 'Antoine de Saint-Exupéry',
                'isbn': '9780156013987',
                'genre': 'children',
                'category': categories['children'],
                'price': 9.99,
                'description': 'A poetic tale about a young prince who visits various planets in space.',
                'publication_year': 1943,
                'publisher': 'Harcourt',
                'page_count': 96
            },
            {
                'title': 'Where the Wild Things Are',
                'author': 'Maurice Sendak',
                'isbn': '9780060254926',
                'genre': 'children',
                'category': categories['children'],
                'price': 8.99,
                'description': 'The story of Max, a young boy who sails to an island inhabited by monsters.',
                'publication_year': 1963,
                'publisher': 'Harper & Row',
                'page_count': 48
            }
        ]
        
        for book_data in books_data:
            book, created = Book.objects.get_or_create(
                isbn=book_data['isbn'],
                defaults=book_data
            )
            if created:
                self.stdout.write(f'Created book: {book.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        ) 