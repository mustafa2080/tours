/**
 * Direct Price Fix Script
 * This script directly sets the prices in the payment page
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Direct price fix script loaded');

    // This script is disabled to prevent overriding server-calculated values
    console.log('Price fix script is disabled to prevent overriding server-calculated values');

    // Instead, we'll log the current values on the page for debugging
    logCurrentPriceValues();
});

/**
 * Directly update all price elements - DISABLED
 */
function directUpdatePriceElements(subtotal, discount, total) {
    console.log('directUpdatePriceElements is disabled to prevent overriding server-calculated values');
    return;
}

/**
 * Update an element by ID - DISABLED
 */
function updateElementById(id, value) {
    console.log(`updateElementById is disabled to prevent overriding server-calculated values for ${id}`);
    return;
}

/**
 * Update elements by data-price attribute - DISABLED
 */
function updateElementsByDataAttribute(type, value) {
    console.log(`updateElementsByDataAttribute is disabled to prevent overriding server-calculated values for ${type}`);
    return;
}

/**
 * Log current price values on the page
 */
function logCurrentPriceValues() {
    // Get elements by ID
    const subtotalDisplay = document.getElementById('subtotal-display');
    const discountDisplay = document.getElementById('discount-display');
    const totalDisplay = document.getElementById('total-display');
    const discountAmount = document.getElementById('discount-amount');

    // Log values
    console.log('Current price values on the page:');
    if (subtotalDisplay) console.log('subtotal-display:', subtotalDisplay.textContent);
    if (discountDisplay) console.log('discount-display:', discountDisplay.textContent);
    if (totalDisplay) console.log('total-display:', totalDisplay.textContent);
    if (discountAmount) console.log('discount-amount:', discountAmount.textContent);
}

/**
 * Update Alpine.js data - DISABLED
 */
function updateAlpineData(subtotal, discount, total) {
    console.log('updateAlpineData is disabled to prevent overriding server-calculated values');
    return;
}
