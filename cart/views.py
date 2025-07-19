from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Cart, CartItem
from books.models import Book

@login_required
def cart_detail(request):
    """Show the user's shopping cart"""
    # Get or create user's cart
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = user_cart.items.all()
    
    context = {
        'cart': user_cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
@require_POST
def add_to_cart(request):
    """Add a book to the shopping cart (AJAX)"""
    book_id = request.POST.get('book_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        # Get the book
        selected_book = Book.objects.get(id=book_id)
        
        # Get or create user's cart
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if book is already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            book=selected_book,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Book already in cart, increase quantity
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{selected_book.title} added to cart successfully!',
            'cart_count': user_cart.item_count,
            'cart_total': str(user_cart.total_price)
        })
    
    except Book.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Book not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error adding book to cart.'
        })

@login_required
@require_POST
def update_cart_item(request):
    """Change quantity of item in cart (AJAX)"""
    item_id = request.POST.get('item_id')
    new_quantity = int(request.POST.get('quantity', 1))
    
    try:
        # Get the cart item
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        user_cart = cart_item.cart
        
        if new_quantity <= 0:
            # Remove item if quantity is 0 or less
            book_title = cart_item.book.title
            cart_item.delete()
            message = 'Item removed from cart.'
            item_total = '0.00'
        else:
            # Update quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            message = 'Cart updated successfully!'
            item_total = str(cart_item.total_price)
        
        # Get fresh cart data after changes
        try:
            # Get the cart again to ensure we have fresh data
            user_cart = Cart.objects.get(user=request.user)
            cart_total = str(user_cart.total_price)
            cart_count = user_cart.item_count
        except Cart.DoesNotExist:
            # Cart was deleted, create new one
            user_cart = Cart.objects.create(user=request.user)
            cart_total = '0.00'
            cart_count = 0
        
        return JsonResponse({
            'success': True,
            'message': message,
            'item_total': item_total,
            'cart_total': cart_total,
            'cart_count': cart_count
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cart item not found.'
        })
    except Exception as e:
        print(f"Error in update_cart_item: {e}")  # Debug print
        return JsonResponse({
            'success': False,
            'message': 'Error updating cart.'
        })

@login_required
@require_POST
def remove_from_cart(request):
    """Remove an item from the cart (AJAX)"""
    item_id = request.POST.get('item_id')
    
    try:
        # Get the cart item
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        book_title = cart_item.book.title
        
        # Get cart info before deleting
        user_cart = cart_item.cart
        
        # Remove the item
        cart_item.delete()
        
        # Refresh cart from database
        try:
            user_cart.refresh_from_db()
        except:
            # If cart doesn't exist anymore, create a new one
            user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'{book_title} removed from cart.',
            'cart_total': str(user_cart.total_price),
            'cart_count': user_cart.item_count
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Cart item not found.'
        })
    except Exception as e:
        print(f"Error in remove_from_cart: {e}")  # Debug print
        return JsonResponse({
            'success': False,
            'message': 'Error removing item from cart.'
        })

@login_required
@require_POST
def clear_cart(request):
    """Remove all items from the cart (AJAX)"""
    try:
        # Get user's cart (create if doesn't exist)
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Remove all items from cart
        deleted_count = user_cart.items.count()
        user_cart.items.all().delete()
        
        print(f"Cleared {deleted_count} items from cart for user {request.user.username}")  # Debug
        
        return JsonResponse({
            'success': True,
            'message': f'Cart cleared successfully! Removed {deleted_count} items.',
            'cart_total': '0.00',
            'cart_count': 0
        })
    
    except Exception as e:
        print(f"Error in clear_cart: {e}")  # Debug print
        return JsonResponse({
            'success': False,
            'message': f'Error clearing cart: {str(e)}'
        })

@login_required
def checkout(request):
    """Process the checkout (simulated)"""
    user_cart = request.user.cart
    
    # Check if cart is empty
    if not user_cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        # Simulate checkout process
        # In a real app, this would connect to a payment system
        
        # Clear the cart after successful checkout
        user_cart.items.all().delete()
        
        messages.success(request, 'Order placed successfully! Your books are ready for download.')
        return redirect('home')
    
    context = {
        'cart': user_cart,
        'cart_items': user_cart.items.all(),
    }
    return render(request, 'cart/checkout.html', context)

@login_required
def add_and_redirect(request, book_id):
    """Add a book to cart and go to cart page (for non-AJAX button)"""
    try:
        # Get the book
        selected_book = Book.objects.get(id=book_id)
        
        # Get or create user's cart
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Add book to cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            book=selected_book,
            defaults={'quantity': 1}
        )
        
        if not created:
            # Book already in cart, increase quantity
            cart_item.quantity += 1
            cart_item.save()
            
        messages.success(request, f'"{selected_book.title}" added to your eBook cart!')
        
    except Book.DoesNotExist:
        messages.error(request, 'Book not found.')
        
    return redirect('cart:cart_detail')
