/**
 * Booking Steps JavaScript
 * This script handles the multi-step booking confirmation process
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Booking steps script loaded');

    // Make sure Alpine.js is available
    if (typeof Alpine === 'undefined') {
        console.error('Alpine.js is not loaded');
        const container = document.querySelector('[x-data="bookingConfirmation()"]');
        if (container) {
            container.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong class="font-bold">Error!</strong>
                    <span class="block sm:inline">Alpine.js is not loaded. Please refresh the page.</span>
                </div>
            `;
        }
        return;
    }

    // Initialize when Alpine.js is ready
    document.addEventListener('alpine:init', () => {
        // Wait a short moment for Alpine.js to fully initialize
        setTimeout(() => {
            const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
            if (bookingFormEl && bookingFormEl.__x) {
                initializeBookingForm(bookingFormEl);
            }
        }, 100);
    });
});

/**
 * Initialize the booking form
 * @param {HTMLElement} bookingFormEl - The booking form element
 */
function initializeBookingForm(bookingFormEl) {
    // Initialize progress bar
    initProgressBar();

    // Setup step navigation
    setupStepNavigation();

    // Ensure price elements are visible
    ensurePriceElementsVisible();

    // Initialize payment methods if we're on step 2
    if (bookingFormEl.__x.$data.currentStep === 2) {
        initializePaymentMethods(bookingFormEl);
    }

    // Watch for step changes
    bookingFormEl.__x.$watch('currentStep', (value) => {
        // Update progress bar
        updateProgressBar(value);

        // Initialize payment methods when reaching step 2
        if (value === 2) {
            initializePaymentMethods(bookingFormEl);
        }

        // Mark previous steps as completed
        for (let i = 1; i < value; i++) {
            markStepAsCompleted(i);
        }

        // Mark current step as active
        markStepAsActive(value);

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Initialize payment methods
 * @param {HTMLElement} bookingFormEl - The booking form element
 */
function initializePaymentMethods(bookingFormEl) {
    const bookingId = bookingFormEl.querySelector('[data-booking-id]')?.getAttribute('data-booking-id');
    if (!bookingId) return;

    const data = bookingFormEl.__x.$data;
    const amount = data.totalPrice;
    const currencyCode = data.currencyCode || 'USD';

    // Initialize PayPal if SDK is loaded
    if (typeof paypal !== 'undefined') {
        const paypalContainer = document.getElementById('paypal-button-container');
        if (paypalContainer) {
            paypal.Buttons({
                createOrder: async function() {
                    const response = await fetch(`/booking/${bookingId}/payment/paypal/create/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken()
                        }
                    });
                    const orderData = await response.json();
                    return orderData.id;
                },
                onApprove: async function(data) {
                    bookingFormEl.__x.$data.isProcessing = true;
                    try {
                        const response = await fetch(`/booking/${bookingId}/payment/paypal/capture/`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken()
                            },
                            body: JSON.stringify({
                                order_id: data.orderID
                            })
                        });
                        const captureData = await response.json();
                        if (captureData.success) {
                            bookingFormEl.__x.$data.transactionId = captureData.transaction_id;
                            bookingFormEl.__x.$data.currentStep = 3;
                        } else {
                            throw new Error(captureData.error || 'Payment failed');
                        }
                    } catch (error) {
                        showPaymentError(error.message);
                    } finally {
                        bookingFormEl.__x.$data.isProcessing = false;
                    }
                }
            }).render('#paypal-button-container');
        }
    }
}

/**
 * Make sure all price elements are visible
 */
function ensurePriceElementsVisible() {
    const priceElements = [
        'subtotal', 'total', 'discount'
    ];

    priceElements.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'inline-block';
            element.style.minWidth = '80px';
            element.style.textAlign = 'right';
        }
    });
}

/**
 * Update progress bar
 * @param {number} step - The current step (1-based)
 */
function updateProgressBar(step) {
    const width = ((step - 1) / 2) * 100;
    const progressBar = document.querySelector('.progress-bar-fill');
    if (progressBar) {
        progressBar.style.width = `${width}%`;
        if (step === 3) {
            progressBar.classList.add('success-animation');
        } else {
            progressBar.classList.remove('success-animation');
        }
    }
}

/**
 * Mark step as completed
 * @param {number} step - The step to mark as completed (1-based)
 */
function markStepAsCompleted(step) {
    const stepElement = document.querySelector(`.progress-step:nth-child(${step})`);
    if (stepElement) {
        stepElement.classList.add('completed');
        stepElement.classList.remove('active');
        
        // Update step content
        stepElement.innerHTML = '<i class="fas fa-check text-white"></i>';
    }
}

/**
 * Mark step as active
 * @param {number} step - The step to mark as active (1-based)
 */
function markStepAsActive(step) {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach((el, index) => {
        // Convert to 1-based index
        const stepNum = index + 1;
        
        if (stepNum === step) {
            el.classList.add('active');
            el.classList.remove('completed');
            el.innerHTML = `<span class="text-white">${step}</span>`;
        } else if (stepNum > step) {
            el.classList.remove('active', 'completed');
            el.innerHTML = `<span class="text-gray-500">${stepNum}</span>`;
        }
    });
}

/**
 * Show payment error message
 * @param {string} message - The error message to display
 */
function showPaymentError(message) {
    const errorElement = document.querySelector('[x-text="paymentErrorMessage"]');
    if (errorElement) {
        const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
        if (bookingFormEl && bookingFormEl.__x) {
            bookingFormEl.__x.$data.paymentErrorMessage = message;
        }
    }
}

/**
 * Get CSRF token from cookies
 * @returns {string} The CSRF token
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
