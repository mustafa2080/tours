/**
 * Price Display Fix Script
 * This script ensures that price elements are always visible in all pages
 */

// Function to fix price display
function fixPriceDisplay() {
    console.log('Fixing price display');
    
    // Get all price elements
    const priceElements = document.querySelectorAll('[data-price], #payment-subtotal, #payment-total, #payment-discount, #subtotal, #total, #discount');
    
    // Make sure they are visible
    priceElements.forEach(function(element) {
        if (element) {
            // Set inline styles with !important
            element.setAttribute('style', 'display: inline-block !important; min-width: 80px !important; text-align: right !important;');
            
            // Add a class for additional styling
            element.classList.add('price-element-fixed');
            
            // Make sure the element has content
            if (!element.textContent || element.textContent.trim() === '') {
                // Try to get the value from Alpine.js
                const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
                if (bookingFormEl && bookingFormEl.__x) {
                    const data = bookingFormEl.__x.$data;
                    
                    // Determine which price to show based on the element ID or data-price attribute
                    let price = 0;
                    let currencyCode = data.currency || 'USD';
                    
                    if (element.id.includes('subtotal') || element.getAttribute('data-price') === 'subtotal') {
                        price = data.subtotal || 0;
                    } else if (element.id.includes('discount') || element.getAttribute('data-price') === 'discount') {
                        price = data.discountAmount || 0;
                    } else if (element.id.includes('total') || element.getAttribute('data-price') === 'total') {
                        price = data.totalPrice || 0;
                    }
                    
                    // Format the price
                    element.textContent = price.toFixed(2) + ' ' + currencyCode;
                } else {
                    // Fallback - set a placeholder value
                    element.textContent = '0.00 USD';
                }
            }
        }
    });
    
    // Make sure payment section is visible
    const paymentSection = document.getElementById('payment-section');
    if (paymentSection) {
        paymentSection.style.display = 'block';
    }
    
    // Make sure PayPal button container is visible
    const paypalButtonContainer = document.getElementById('paypal-button-container');
    if (paypalButtonContainer) {
        paypalButtonContainer.style.display = 'block';
        paypalButtonContainer.style.minHeight = '200px';
    }
}

// Run the fix when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Price display fix script loaded');
    
    // Fix price display immediately
    fixPriceDisplay();
    
    // Fix price display after a short delay
    setTimeout(fixPriceDisplay, 500);
    
    // Set an interval to periodically fix price display
    setInterval(fixPriceDisplay, 2000);
    
    // Fix price display when the payment step is shown
    const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        bookingFormEl.__x.$watch('currentStep', function(value) {
            if (value === 2) {
                // We're on the payment step, fix the price display
                fixPriceDisplay();
                setTimeout(fixPriceDisplay, 100);
                setTimeout(fixPriceDisplay, 500);
            }
        });
    }
});

// Add CSS to ensure price elements are visible
document.addEventListener('DOMContentLoaded', function() {
    // Create a style element
    const style = document.createElement('style');
    
    // Add CSS rules
    style.textContent = `
        /* Make sure price elements are always visible */
        [data-price], #payment-subtotal, #payment-total, #payment-discount, #subtotal, #total, #discount {
            display: inline-block !important;
            min-width: 80px !important;
            text-align: right !important;
        }
        
        /* Add a class for additional styling */
        .price-element-fixed {
            display: inline-block !important;
            min-width: 80px !important;
            text-align: right !important;
            background-color: rgba(254, 243, 199, 0.2);
            padding: 2px 4px;
            border-radius: 4px;
        }
        
        /* Make sure payment section is visible */
        #payment-section {
            display: block !important;
        }
        
        /* Make sure PayPal button container is visible */
        #paypal-button-container {
            display: block !important;
            min-height: 200px !important;
        }
    `;
    
    // Append the style element to the head
    document.head.appendChild(style);
});
