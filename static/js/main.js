// ReadEasy - Main JavaScript
$(document).ready(function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Star Rating System
    $('.star-rating input[type="radio"]').change(function() {
        var rating = $(this).val();
        var bookId = $(this).data('book-id');
        
        $.ajax({
            url: '/reviews/rate/',
            method: 'POST',
            data: {
                book_id: bookId,
                rating: rating,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update the displayed rating
                    $('.average-rating').text(response.average_rating);
                    $('.total-ratings').text(response.total_ratings);
                    
                    // Show success message
                    showNotification('Rating submitted successfully!', 'success');
                    
                    // Update star display
                    updateStarDisplay(rating);
                } else {
                    showNotification('Error submitting rating. Please try again.', 'error');
                }
            },
            error: function() {
                showNotification('Error submitting rating. Please try again.', 'error');
            }
        });
    });
    
    // Update star display
    function updateStarDisplay(rating) {
        $('.star-rating label').each(function(index) {
            if (index < rating) {
                $(this).find('i').removeClass('far').addClass('fas');
            } else {
                $(this).find('i').removeClass('fas').addClass('far');
            }
        });
    }
    
    // Add to Cart
    $('.add-to-cart').click(function() {
        var bookId = $(this).data('book-id');
        var button = $(this);
        var originalText = button.html();
        
        // Show loading state
        button.html('<span class="loading"></span>');
        button.prop('disabled', true);
        
        $.ajax({
            url: '/cart/add/',
            method: 'POST',
            data: {
                book_id: bookId,
                quantity: 1,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update cart count
                    updateCartCount(response.cart_count);
                    
                    // Show success message
                    showNotification('Book added to cart!', 'success');
                    
                    // Update button
                    button.html('<i class="fas fa-check"></i>');
                    button.removeClass('btn-outline-success').addClass('btn-success');
                    
                    // Reset button after 2 seconds
                    setTimeout(function() {
                        button.html(originalText);
                        button.removeClass('btn-success').addClass('btn-outline-success');
                        button.prop('disabled', false);
                    }, 2000);
                } else {
                    showNotification('Error adding book to cart. Please try again.', 'error');
                    button.html(originalText);
                    button.prop('disabled', false);
                }
            },
            error: function() {
                showNotification('Error adding book to cart. Please try again.', 'error');
                button.html(originalText);
                button.prop('disabled', false);
            }
        });
    });
    
    // Update Cart Count
    function updateCartCount(count) {
        $('.cart-count').text(count);
        
        // Add animation
        $('.cart-count').addClass('animate__animated animate__bounceIn');
        setTimeout(function() {
            $('.cart-count').removeClass('animate__animated animate__bounceIn');
        }, 1000);
    }
    
    // Update Cart Item Quantity
    $('.update-quantity').change(function() {
        var itemId = $(this).data('item-id');
        var quantity = parseInt($(this).val());
        var select = $(this);
        var cartItem = select.closest('.cart-item');
        
        $.ajax({
            url: '/cart/update/',
            method: 'POST',
            data: {
                item_id: itemId,
                quantity: quantity,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    if (quantity === 0) {
                        // Item was removed, hide the cart item
                        cartItem.fadeOut(300, function() {
                            cartItem.remove();
                            
                            // Check if cart is empty
                            if (response.cart_count == 0) {
                                location.reload();
                            }
                        });
                        showNotification('Item removed from cart!', 'success');
                    } else {
                        // Update item total
                        cartItem.find('.item-total').text('$' + response.item_total);
                        showNotification('Cart updated successfully!', 'success');
                    }
                    
                    // Update cart total
                    $('.cart-total-amount').text('$' + response.cart_total);
                    
                    // Update cart count
                    updateCartCount(response.cart_count);
                } else {
                    showNotification('Error updating cart. Please try again.', 'error');
                }
            },
            error: function(xhr, status, error) {
                showNotification('Error updating cart. Please try again.', 'error');
            }
        });
    });
    
    // Remove from Cart
    $('.remove-from-cart').click(function() {
        var itemId = $(this).data('item-id');
        var bookTitle = $(this).data('book-title');
        var item = $(this).closest('.cart-item');
        
        // Set the book title in the modal
        $('#bookTitleToRemove').text(bookTitle);
        
        // Show the modal
        var removeModal = new bootstrap.Modal(document.getElementById('removeItemModal'));
        removeModal.show();
        
        // Handle confirmation
        $('#confirmRemoveItem').off('click').on('click', function() {
            $.ajax({
                url: '/cart/remove/',
                method: 'POST',
                data: {
                    item_id: itemId,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    console.log('Response:', response); // Debug
                    
                    // Hide the modal first
                    removeModal.hide();
                    
                    // Check if response is a string (needs parsing) or object
                    if (typeof response === 'string') {
                        try {
                            response = JSON.parse(response);
                        } catch (e) {
                            console.log('Failed to parse response:', e);
                        }
                    }
                    
                    // Check if the operation was successful
                    if (response && response.success) {
                        // Animate removal
                        item.fadeOut(300, function() {
                            item.remove();
                            
                            // Update cart total if available
                            if (response.cart_total) {
                                $('.cart-total-amount').text('$' + response.cart_total);
                            }
                            
                            // Update cart count if available
                            if (response.cart_count !== undefined) {
                                updateCartCount(response.cart_count);
                                
                                // Check if cart is empty
                                if (response.cart_count == 0) {
                                    location.reload();
                                }
                            }
                        });
                        
                        showNotification('Item removed from cart!', 'success');
                    } else {
                        showNotification('Error removing item. Please try again.', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    console.log('Error:', xhr.responseText); // Debug
                    removeModal.hide();
                    showNotification('Error removing item. Please try again.', 'error');
                }
            });
        });
    });
    
    // Clear Cart
    $('.clear-cart-btn').click(function() {
        // Show the clear cart modal
        var clearCartModal = new bootstrap.Modal(document.getElementById('clearCartModal'));
        clearCartModal.show();
        
        // Handle confirmation
        $('#confirmClearCart').off('click').on('click', function() {
            $.ajax({
                url: '/cart/clear/',
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    console.log('Clear cart response:', response); // Debug
                    
                    // Hide the modal
                    clearCartModal.hide();
                    
                    if (response.success) {
                        // Update cart total and count
                        $('.cart-total-amount').text('$' + response.cart_total);
                        updateCartCount(response.cart_count);
                        
                        // Show success message
                        showNotification(response.message, 'success');
                        
                        // Reload the page to show empty cart
                        location.reload();
                    } else {
                        showNotification('Error clearing cart. Please try again.', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    console.log('Clear cart error:', xhr.responseText); // Debug
                    clearCartModal.hide();
                    showNotification('Error clearing cart. Please try again.', 'error');
                }
            });
        });
    });
    
    // Search with debouncing
    var searchTimeout;
    $('input[name="q"]').on('input', function() {
        clearTimeout(searchTimeout);
        var query = $(this).val();
        
        searchTimeout = setTimeout(function() {
            if (query.length >= 2) {
                performSearch(query);
            }
        }, 500);
    });
    
    // Perform search
    function performSearch(query) {
        $.ajax({
            url: '/books/search/',
            method: 'GET',
            data: { q: query },
            success: function(response) {
                $('#books-container').html(response);
            },
            error: function() {
                showNotification('Error performing search. Please try again.', 'error');
            }
        });
    }
    
    // Book Preview
    $('.show-book-preview').click(function() {
        var bookId = $(this).data('book-id');
        
        // Show the modal
        var previewModal = new bootstrap.Modal(document.getElementById('bookPreviewModal'));
        previewModal.show();
        
        // Load preview content via AJAX
        $.ajax({
            url: '/books/preview/' + bookId + '/',
            method: 'GET',
            success: function(response) {
                $('#bookPreviewModal .modal-body').html(response);
            },
            error: function() {
                $('#bookPreviewModal .modal-body').html(
                    '<div class="text-center py-4">' +
                    '<i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>' +
                    '<h5>Preview Not Available</h5>' +
                    '<p class="text-muted">Sorry, the preview for this book is not available at the moment.</p>' +
                    '</div>'
                );
            }
        });
    });

    // Wishlist Toggle
    $('.wishlist-toggle').click(function() {
        var bookId = $(this).data('book-id');
        var button = $(this);
        var icon = button.find('i');
        
        $.ajax({
            url: '/books/toggle-wishlist/',
            method: 'POST',
            data: {
                book_id: bookId,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    if (response.in_wishlist) {
                        icon.removeClass('far').addClass('fas text-danger');
                        showNotification('Added to wishlist!', 'success');
                    } else {
                        icon.removeClass('fas text-danger').addClass('far');
                        showNotification('Removed from wishlist!', 'success');
                    }
                } else {
                    showNotification('Error updating wishlist. Please try again.', 'error');
                }
            },
            error: function() {
                showNotification('Error updating wishlist. Please try again.', 'error');
            }
        });
    });
    
    // Show notification
    function showNotification(message, type) {
        // Remove existing notifications
        $('.notification').remove();
        
        // Create notification element
        var notification = $('<div class="notification notification-' + type + '">' + message + '</div>');
        
        // Add to page
        $('body').append(notification);
        
        // Show notification
        notification.addClass('show');
        
        // Hide after 3 seconds
        setTimeout(function() {
            notification.removeClass('show');
            setTimeout(function() {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').click(function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 800);
        }
    });
    
    // Card hover effects
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg');
        },
        function() {
            $(this).removeClass('shadow-lg');
        }
    );
    
    // Form validation
    $('form').on('submit', function() {
        var isValid = true;
        
        $(this).find('input[required], select[required], textarea[required]').each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        return isValid;
    });
    
    // Remove validation classes on input
    $('input, select, textarea').on('input change', function() {
        $(this).removeClass('is-invalid');
    });
    
    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Back to top button
    var backToTop = $('<button class="btn btn-primary back-to-top" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; display: none;"><i class="fas fa-arrow-up"></i></button>');
    $('body').append(backToTop);
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTop.fadeIn();
        } else {
            backToTop.fadeOut();
        }
    });
    
    backToTop.click(function() {
        $('html, body').animate({scrollTop: 0}, 800);
    });
    
    // Initialize animations
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true
    });
});

// CSS for notifications
const notificationStyles = `
<style>
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 9999;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    max-width: 300px;
}

.notification.show {
    transform: translateX(0);
}

.notification-success {
    background-color: var(--success-color);
}

.notification-error {
    background-color: var(--danger-color);
}

.back-to-top {
    border-radius: 50%;
    width: 50px;
    height: 50px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
}

.back-to-top:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.lazy {
    opacity: 0;
    transition: opacity 0.3s;
}

.lazy.loaded {
    opacity: 1;
}

.animate__animated {
    animation-duration: 0.6s;
}

@keyframes bounceIn {
    0% {
        transform: scale(0.3);
        opacity: 0;
    }
    50% {
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        transform: scale(1);
        opacity: 1;
    }
}

.animate__bounceIn {
    animation-name: bounceIn;
}
</style>
`;

// Add styles to head
$('head').append(notificationStyles); 