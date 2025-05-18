// Main JavaScript file for EcoFinds application

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize Bootstrap Popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }

    // Add to cart functionality with AJAX
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Only use AJAX if the form has the data-ajax attribute
            if (form.hasAttribute('data-ajax')) {
                e.preventDefault();
                
                fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Show success message
                        const successAlert = document.createElement('div');
                        successAlert.classList.add('alert', 'alert-success', 'alert-dismissible', 'fade', 'show', 'mt-2');
                        successAlert.innerHTML = `
                            <strong>Success!</strong> Product added to cart!
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        form.parentElement.appendChild(successAlert);
                        
                        // Remove the alert after 3 seconds
                        setTimeout(() => {
                            successAlert.remove();
                        }, 3000);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    });
    
    // Quantity input handling - auto-submit forms when quantity changes
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form && form.hasAttribute('data-auto-submit')) {
                form.submit();
            }
        });
    });

    // Quantity increment/decrement buttons
    document.querySelectorAll('.decrease-qty').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const value = parseInt(input.value);
            if (value > parseInt(input.getAttribute('min') || 1)) {
                input.value = value - 1;
                
                // Auto-submit if needed
                const form = input.closest('form');
                if (form && form.hasAttribute('data-auto-submit')) {
                    form.submit();
                }
            }
        });
    });
    
    document.querySelectorAll('.increase-qty').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            const value = parseInt(input.value);
            if (value < parseInt(input.getAttribute('max') || 10)) {
                input.value = value + 1;
                
                // Auto-submit if needed
                const form = input.closest('form');
                if (form && form.hasAttribute('data-auto-submit')) {
                    form.submit();
                }
            }
        });
    });
    
    // Dismiss alerts automatically after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = new bootstrap.Alert(alert);
            closeButton.close();
        }, 5000);
    });
});