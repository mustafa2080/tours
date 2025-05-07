/**
 * Price Calculator for Tourism Website
 * This script handles the calculation and display of prices in the booking form
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Price calculator initialized');
    
    // Force update of price displays when the page loads
    setTimeout(forceUpdatePrices, 500);
    setTimeout(forceUpdatePrices, 1000);
    setTimeout(forceUpdatePrices, 2000);
    
    // Add event listeners to quantity inputs
    const adultsInput = document.getElementById('id_num_adults');
    const childrenInput = document.getElementById('id_num_children');
    
    if (adultsInput) {
        adultsInput.addEventListener('change', forceUpdatePrices);
    }
    
    if (childrenInput) {
        childrenInput.addEventListener('change', forceUpdatePrices);
    }
    
    // Add event listeners to quantity buttons
    document.querySelectorAll('button[type="button"]').forEach(button => {
        if (button.innerHTML.includes('fa-plus') || button.innerHTML.includes('fa-minus')) {
            button.addEventListener('click', function() {
                setTimeout(forceUpdatePrices, 100);
            });
        }
    });
});

/**
 * Force update of all price displays on the page
 */
function forceUpdatePrices() {
    try {
        console.log('Forcing price update');
        
        // Get the Alpine.js component
        const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
        if (!bookingFormEl || !bookingFormEl.__x) {
            console.warn('Alpine.js component not found');
            return;
        }
        
        const data = bookingFormEl.__x.$data;
        
        // Calculate prices
        const numAdults = parseInt(data.numAdults || 1);
        const numChildren = parseInt(data.numChildren || 0);
        const totalPersons = numAdults + numChildren;
        
        // Get price values
        const basePrice = parseFloat(data.basePrice || 0);
        const discountedPrice = parseFloat(data.discountedPrice || basePrice);
        const hasDiscount = data.hasDiscount || false;
        const currencyCode = data.currency || 'USD';
        
        // Calculate totals
        const subtotal = totalPersons * basePrice;
        const discountPerPerson = basePrice - discountedPrice;
        const discountAmount = hasDiscount ? totalPersons * discountPerPerson : 0;
        const totalPrice = hasDiscount ? totalPersons * discountedPrice : subtotal;
        
        console.log('Calculated prices:', {
            numAdults,
            numChildren,
            totalPersons,
            basePrice,
            discountedPrice,
            hasDiscount,
            subtotal,
            discountAmount,
            totalPrice,
            currencyCode
        });
        
        // Format prices
        const formattedSubtotal = formatCurrency(subtotal, currencyCode);
        const formattedDiscount = hasDiscount ? '-' + formatCurrency(discountAmount, currencyCode) : '';
        const formattedTotal = formatCurrency(totalPrice, currencyCode);
        
        console.log('Formatted prices:', {
            formattedSubtotal,
            formattedDiscount,
            formattedTotal
        });
        
        // Update DOM elements
        updatePriceElements('subtotal', formattedSubtotal);
        if (hasDiscount) {
            updatePriceElements('discount', formattedDiscount);
        }
        updatePriceElements('total', formattedTotal);
        
        // Update amounts in invoice table
        const adultAmount = document.querySelector('.adult-amount');
        if (adultAmount) {
            adultAmount.innerHTML = formatCurrency(numAdults * discountedPrice, currencyCode);
        }
        
        const childAmount = document.querySelector('.child-amount');
        if (childAmount && numChildren > 0) {
            childAmount.innerHTML = formatCurrency(numChildren * discountedPrice, currencyCode);
        }
        
        // Update "Based on" text
        updateBasedOnText(numAdults, numChildren);
        
        // Add highlight effect to price elements
        addHighlightEffect();
    } catch (error) {
        console.error('Error in forceUpdatePrices:', error);
    }
}

/**
 * Update all price elements with the given type
 */
function updatePriceElements(type, value) {
    const elements = document.querySelectorAll(`[data-price="${type}"]`);
    console.log(`Updating ${elements.length} ${type} elements with value: ${value}`);
    
    elements.forEach(element => {
        element.innerHTML = value;
    });
}

/**
 * Format a currency value
 */
function formatCurrency(amount, currencyCode) {
    try {
        // Handle invalid input
        if (amount === undefined || amount === null || isNaN(amount)) {
            console.warn('Invalid amount for formatCurrency:', amount);
            amount = 0;
        }
        
        // Force amount to be a number
        amount = Number(amount);
        
        // Simple formatting fallback first
        let formattedAmount = amount.toFixed(2);
        
        try {
            // More robust currency formatting using Intl.NumberFormat
            formattedAmount = new Intl.NumberFormat(undefined, {
                style: 'decimal',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(amount);
        } catch (formatError) {
            console.warn('Error using Intl.NumberFormat, using fallback:', formatError);
        }
        
        return formattedAmount + ' ' + currencyCode;
    } catch (error) {
        console.error('Error formatting currency:', error);
        return amount.toFixed(2) + ' ' + currencyCode;
    }
}

/**
 * Update the "Based on" text
 */
function updateBasedOnText(numAdults, numChildren) {
    const basedOnElements = document.querySelectorAll('.price-summary p');
    basedOnElements.forEach(element => {
        if (element.textContent.includes('Based on')) {
            const childrenText = numChildren > 0 ? ` and ${numChildren} children` : '';
            element.innerHTML = `Based on ${numAdults} adults${childrenText}`;
        }
    });
}

/**
 * Add highlight effect to price elements
 */
function addHighlightEffect() {
    // Add a class to highlight price sections
    document.querySelectorAll('.price-summary').forEach(element => {
        element.classList.add('price-updated');
        
        // Remove the class after animation completes
        setTimeout(() => {
            element.classList.remove('price-updated');
        }, 2000);
    });
    
    // Add highlight effect to price elements
    document.querySelectorAll('[data-price]').forEach(element => {
        element.classList.remove('bg-yellow-100');
        void element.offsetWidth; // Force reflow
        element.classList.add('bg-yellow-100');
        
        // Remove highlight after animation completes
        setTimeout(() => {
            element.classList.remove('bg-yellow-100');
        }, 1000);
    });
}
