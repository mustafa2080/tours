/**
 * Price Transfer Script
 * This script transfers price values from the tour detail page to the payment page
 */

// Function to store price values in localStorage
function storePriceValues() {
    console.log('Storing price values in localStorage');
    
    // Get price elements from the tour detail page
    const subtotalElement = document.getElementById('subtotal-price');
    const discountElement = document.getElementById('discount-amount');
    const totalElement = document.getElementById('total-price');
    
    // Store values in localStorage
    if (subtotalElement) {
        localStorage.setItem('tour_subtotal', subtotalElement.textContent);
        console.log('Stored subtotal:', subtotalElement.textContent);
    }
    
    if (discountElement) {
        localStorage.setItem('tour_discount', discountElement.textContent);
        console.log('Stored discount:', discountElement.textContent);
    }
    
    if (totalElement) {
        localStorage.setItem('tour_total', totalElement.textContent);
        console.log('Stored total:', totalElement.textContent);
    }
}

// Function to retrieve price values from localStorage and update the payment page
function retrieveAndUpdatePriceValues() {
    console.log('Retrieving price values from localStorage');
    
    // Get stored values
    const subtotal = localStorage.getItem('tour_subtotal');
    const discount = localStorage.getItem('tour_discount');
    const total = localStorage.getItem('tour_total');
    
    console.log('Retrieved values:', { subtotal, discount, total });
    
    // Update payment page elements
    updatePaymentElement('payment-subtotal', subtotal);
    updatePaymentElement('payment-discount', discount);
    updatePaymentElement('payment-total', total);
    
    // Also update elements with data-price attribute
    updateDataPriceElements('subtotal', subtotal);
    updateDataPriceElements('discount', discount);
    updateDataPriceElements('total', total);
    
    // Update Alpine.js data if available
    updateAlpineData(subtotal, discount, total);
}

// Function to update a payment element with a value
function updatePaymentElement(elementId, value) {
    const element = document.getElementById(elementId);
    if (element && value) {
        element.textContent = value;
        element.style.display = 'inline-block';
        element.style.minWidth = '80px';
        element.style.textAlign = 'right';
        console.log(`Updated ${elementId} with ${value}`);
    }
}

// Function to update elements with data-price attribute
function updateDataPriceElements(priceType, value) {
    const elements = document.querySelectorAll(`[data-price="${priceType}"]`);
    elements.forEach(function(element) {
        if (element && value) {
            element.textContent = value;
            element.style.display = 'inline-block';
            element.style.minWidth = '80px';
            element.style.textAlign = 'right';
            console.log(`Updated data-price="${priceType}" with ${value}`);
        }
    });
}

// Function to update Alpine.js data
function updateAlpineData(subtotal, discount, total) {
    const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        const data = bookingFormEl.__x.$data;
        
        // Parse values
        if (subtotal) {
            const subtotalValue = parseFloat(subtotal.replace(/[^0-9.-]+/g, ''));
            if (!isNaN(subtotalValue)) {
                data.subtotal = subtotalValue;
                console.log('Updated Alpine.js subtotal:', subtotalValue);
            }
        }
        
        if (discount) {
            const discountValue = parseFloat(discount.replace(/[^0-9.-]+/g, ''));
            if (!isNaN(discountValue)) {
                data.discountAmount = Math.abs(discountValue);
                data.hasDiscount = true;
                console.log('Updated Alpine.js discount:', Math.abs(discountValue));
            }
        }
        
        if (total) {
            const totalValue = parseFloat(total.replace(/[^0-9.-]+/g, ''));
            if (!isNaN(totalValue)) {
                data.totalPrice = totalValue;
                console.log('Updated Alpine.js total:', totalValue);
            }
        }
        
        // Extract currency code
        if (total) {
            const currencyMatch = total.match(/[A-Z]{3}/);
            if (currencyMatch) {
                data.currency = currencyMatch[0];
                console.log('Updated Alpine.js currency:', currencyMatch[0]);
            }
        }
    }
}

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Price transfer script loaded');
    
    // Check if we're on the tour detail page
    const bookTourButtons = document.querySelectorAll('a[href*="booking/create"]');
    if (bookTourButtons.length > 0) {
        console.log('On tour detail page, setting up price storage');
        
        // Store price values when a "Book Tour" button is clicked
        bookTourButtons.forEach(function(button) {
            button.addEventListener('click', storePriceValues);
        });
    }
    
    // Check if we're on the payment page
    const paymentSection = document.getElementById('payment-section');
    if (paymentSection) {
        console.log('On payment page, retrieving stored price values');
        
        // Retrieve and update price values
        retrieveAndUpdatePriceValues();
        
        // Also update when the payment step is shown
        const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
        if (bookingFormEl && bookingFormEl.__x) {
            bookingFormEl.__x.$watch('currentStep', function(value) {
                if (value === 2) {
                    // We're on the payment step, update the prices
                    retrieveAndUpdatePriceValues();
                    
                    // Update again after a short delay
                    setTimeout(retrieveAndUpdatePriceValues, 500);
                }
            });
        }
    }
});
