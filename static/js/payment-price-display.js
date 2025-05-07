/**
 * Payment Price Display Script
 * This script ensures that price elements are always visible in the payment page
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Payment price display script loaded');
    
    // Force update price display when the page loads
    updatePaymentPriceDisplay();
    
    // Set an interval to check and update price display
    setInterval(updatePaymentPriceDisplay, 1000);
});

// Update price display in the payment section
function updatePaymentPriceDisplay() {
    // Get price elements
    const priceElements = [
        'payment-subtotal',
        'payment-total',
        'payment-discount',
        'subtotal',
        'total',
        'discount'
    ];
    
    // Make sure they are visible
    priceElements.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'inline-block';
            element.style.minWidth = '80px';
            element.style.textAlign = 'right';
        }
    });
    
    // Also check for elements with data-price attribute
    document.querySelectorAll('[data-price]').forEach(function(element) {
        element.style.display = 'inline-block';
        element.style.minWidth = '80px';
        element.style.textAlign = 'right';
    });
}

// Function to update all price displays when the payment step is shown
function updatePricesOnPaymentStep() {
    console.log('Updating prices on payment step');
    
    // Get the Alpine.js component
    const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        // Get the data from Alpine.js
        const data = bookingFormEl.__x.$data;
        
        // Update the payment price elements
        const subtotalElement = document.getElementById('payment-subtotal');
        const discountElement = document.getElementById('payment-discount');
        const totalElement = document.getElementById('payment-total');
        
        if (subtotalElement && data.subtotal !== undefined) {
            subtotalElement.textContent = formatCurrency(data.subtotal, data.currency);
        }
        
        if (discountElement && data.discountAmount !== undefined) {
            discountElement.textContent = formatCurrency(data.discountAmount, data.currency);
        }
        
        if (totalElement && data.totalPrice !== undefined) {
            totalElement.textContent = formatCurrency(data.totalPrice, data.currency);
        }
    }
}

// Helper function to format currency
function formatCurrency(amount, currencyCode) {
    if (typeof amount !== 'number') {
        try {
            amount = parseFloat(amount);
        } catch (e) {
            amount = 0;
        }
    }
    
    // Format with 2 decimal places
    const formattedAmount = amount.toFixed(2);
    
    // Add currency code
    return `${formattedAmount} ${currencyCode || 'USD'}`;
}

// Watch for changes to the current step in Alpine.js
document.addEventListener('DOMContentLoaded', function() {
    // Get the Alpine.js component
    const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        // Watch for changes to the currentStep
        bookingFormEl.__x.$watch('currentStep', function(value) {
            if (value === 2) {
                // We're on the payment step, update the prices
                updatePricesOnPaymentStep();
                
                // Also make sure the payment section is visible
                const paymentSection = document.getElementById('payment-section');
                if (paymentSection) {
                    paymentSection.style.display = 'block';
                }
            }
        });
    }
});
