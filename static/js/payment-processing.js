/**
 * Payment Processing JavaScript
 * This script handles payment processing for bookings
 */

// PayPal Integration
function initPayPalButtons(bookingId, amount, currencyCode) {
    // Check if PayPal SDK is loaded
    if (typeof paypal === 'undefined') {
        console.error('PayPal SDK not loaded');
        return;
    }

    // Get the PayPal button container
    const paypalButtonContainer = document.getElementById('paypal-button-container');
    if (!paypalButtonContainer) {
        console.error('PayPal button container not found');
        return;
    }

    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');

    // Clear any existing buttons
    paypalButtonContainer.innerHTML = '';

    // Render the PayPal buttons
    paypal.Buttons({
        // Set up the transaction
        createOrder: function(data, actions) {
            // Show loading state
            document.getElementById('paypal-button-container').innerHTML = `
                <div class="bg-gray-50 p-4 rounded-lg text-center text-gray-500">
                    <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
                    Creating PayPal order...
                </div>
            `;

            // Call your server to create the order
            return fetch(`/booking/${bookingId}/payment/paypal/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(orderData) {
                if (orderData.error) {
                    throw new Error(orderData.error);
                }
                return orderData.id;
            });
        },

        // Finalize the transaction
        onApprove: function(data, actions) {
            // Show loading state
            document.getElementById('paypal-processing').classList.remove('hidden');

            // Call your server to capture the order
            return fetch(`/booking/${bookingId}/payment/paypal/capture/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    order_id: data.orderID
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(captureData) {
                if (captureData.error) {
                    throw new Error(captureData.error);
                }

                // Payment successful - update UI
                if (bookingFormEl && bookingFormEl.__x) {
                    // Access the Alpine.js component and update the currentStep
                    bookingFormEl.__x.$data.currentStep = 3;

                    // Update transaction ID
                    bookingFormEl.__x.$data.transactionId = captureData.transaction_id || data.orderID;

                    // Update isProcessing state
                    bookingFormEl.__x.$data.isProcessing = false;

                    // Update progress bar to 100%
                    bookingFormEl.__x.$data.updateProgressBar(3);

                    // Mark previous steps as completed
                    bookingFormEl.__x.$data.markStepAsCompleted(1);
                    bookingFormEl.__x.$data.markStepAsCompleted(2);

                    // Mark current step as active
                    bookingFormEl.__x.$data.markStepAsActive(3);

                    // Add success animation to step 3
                    const step3 = document.querySelector('.progress-step:nth-child(3)');
                    if (step3) {
                        step3.classList.add('success-animation');
                    }
                } else {
                    // Fallback if Alpine.js component is not accessible
                    window.location.href = `/booking/${bookingId}/steps/?step=3&transaction_id=${captureData.transaction_id || data.orderID}`;
                }
            })
            .catch(function(error) {
                console.error('Error capturing PayPal payment:', error);
                showPaymentError('Failed to complete payment. Please try again or contact support.');

                // Hide processing indicator
                document.getElementById('paypal-processing').classList.add('hidden');

                // Reset PayPal buttons
                initPayPalButtons(bookingId, amount, currencyCode);
            });
        },

        // Handle errors
        onError: function(err) {
            console.error('PayPal error:', err);
            showPaymentError('An error occurred with PayPal. Please try again or use a different payment method.');

            // Reset PayPal buttons
            initPayPalButtons(bookingId, amount, currencyCode);
        },

        // Customize button style
        style: {
            layout: 'vertical',
            color: 'blue',
            shape: 'rect',
            label: 'pay',
            height: 50
        }
    }).render('#paypal-button-container');
}

// Credit Card Processing
function processCreditCardPayment(bookingId) {
    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
    if (!bookingFormEl || !bookingFormEl.__x) {
        console.error('Alpine.js component not found');
        showPaymentError('An error occurred. Please refresh the page and try again.');
        return;
    }

    // Use the Alpine.js component's method if available
    if (typeof bookingFormEl.__x.$data.processCreditCardPayment === 'function') {
        bookingFormEl.__x.$data.processCreditCardPayment(bookingId);
        return;
    }

    // Fallback implementation if the Alpine.js component doesn't have the method
    // Get card details from Alpine.js component
    const cardData = {
        card_number: bookingFormEl.__x.$data.cardNumber.replace(/\s/g, ''),
        card_expiry: bookingFormEl.__x.$data.cardExpiry,
        card_cvc: bookingFormEl.__x.$data.cardCvc,
        card_holder_name: bookingFormEl.__x.$data.cardHolderName
    };

    // Validate card details
    if (!bookingFormEl.__x.$data.validateCardDetails()) {
        // Reset processing state
        bookingFormEl.__x.$data.isProcessing = false;
        const cardButton = document.querySelector('button[data-payment-method="card"]');
        const processingElement = document.getElementById('card-processing');
        resetCardButton(cardButton, processingElement);
        return;
    }

    // Show processing state
    document.getElementById('card-processing').classList.remove('hidden');

    // Call your server to process the payment
    fetch(`/booking/${bookingId}/payment/card/process/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(cardData)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            throw new Error(data.error);
        }

        // Payment successful - update UI
        bookingFormEl.__x.$data.currentStep = 3;
        bookingFormEl.__x.$data.transactionId = data.transaction_id;
        bookingFormEl.__x.$data.isProcessing = false;

        // Update progress bar to 100%
        bookingFormEl.__x.$data.updateProgressBar(3);

        // Mark previous steps as completed
        bookingFormEl.__x.$data.markStepAsCompleted(1);
        bookingFormEl.__x.$data.markStepAsCompleted(2);

        // Mark current step as active
        bookingFormEl.__x.$data.markStepAsActive(3);

        // Add success animation to step 3
        const step3 = document.querySelector('.progress-step:nth-child(3)');
        if (step3) {
            step3.classList.add('success-animation');
        }
    })
    .catch(function(error) {
        console.error('Error processing credit card payment:', error);
        showPaymentError(error.message || 'Failed to process payment. Please check your card details and try again.');

        // Reset processing state
        bookingFormEl.__x.$data.isProcessing = false;
        const cardButton = document.querySelector('button[data-payment-method="card"]');
        const processingElement = document.getElementById('card-processing');
        resetCardButton(cardButton, processingElement);
    });
}

// Bank Transfer Processing
function processBankTransfer(bookingId) {
    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
    if (!bookingFormEl || !bookingFormEl.__x) {
        console.error('Alpine.js component not found');
        showPaymentError('An error occurred. Please refresh the page and try again.');
        return;
    }

    // Use the Alpine.js component's method if available
    if (typeof bookingFormEl.__x.$data.processBankTransfer === 'function') {
        bookingFormEl.__x.$data.processBankTransfer(bookingId);
        return;
    }

    // Fallback implementation if the Alpine.js component doesn't have the method
    // Show processing state
    const bankButton = document.querySelector('button[data-payment-method="bank"]');
    if (bankButton) {
        bankButton.disabled = true;
        bankButton.innerHTML = '<div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div> Processing...';
    }

    // Call your server to process the bank transfer
    fetch(`/booking/${bookingId}/payment/bank/process/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            throw new Error(data.error);
        }

        // Payment initiated - update UI
        bookingFormEl.__x.$data.currentStep = 3;
        bookingFormEl.__x.$data.transactionId = data.reference_number;
        bookingFormEl.__x.$data.isProcessing = false;

        // Update progress bar to 100%
        bookingFormEl.__x.$data.updateProgressBar(3);

        // Mark previous steps as completed
        bookingFormEl.__x.$data.markStepAsCompleted(1);
        bookingFormEl.__x.$data.markStepAsCompleted(2);

        // Mark current step as active
        bookingFormEl.__x.$data.markStepAsActive(3);

        // Add success animation to step 3
        const step3 = document.querySelector('.progress-step:nth-child(3)');
        if (step3) {
            step3.classList.add('success-animation');
        }
    })
    .catch(function(error) {
        console.error('Error processing bank transfer:', error);
        showPaymentError(error.message || 'Failed to initiate bank transfer. Please try again or contact support.');

        // Reset processing state
        bookingFormEl.__x.$data.isProcessing = false;
        if (bankButton) {
            bankButton.disabled = false;
            bankButton.innerHTML = '<i class="fas fa-check-circle mr-2"></i> Confirm Bank Transfer Payment';
        }
    });
}

// Helper Functions
function getCsrfToken() {
    // Get CSRF token from cookie
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || '';
}

function showPaymentError(message) {
    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        // Use the Alpine.js component's method
        bookingFormEl.__x.$data.showPaymentError(message);
        return;
    }

    // Fallback if Alpine.js component is not accessible
    // Show payment error message
    const errorElement = document.getElementById('payment-error');
    if (errorElement) {
        if (errorElement.querySelector('span')) {
            errorElement.querySelector('span').textContent = message;
        } else {
            errorElement.innerHTML = `<div class="flex items-center"><i class="fas fa-exclamation-circle mr-2"></i> ${message}</div>`;
        }
        errorElement.classList.remove('hidden');

        // Scroll to error message
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Hide error message after 10 seconds
        setTimeout(() => {
            errorElement.classList.add('hidden');
        }, 10000);
    } else {
        // Fallback to alert if error element not found
        alert(message);
    }
}

function resetCardButton(button, processingElement) {
    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        // Use the Alpine.js component's method
        bookingFormEl.__x.$data.resetCardButton();
        return;
    }

    // Fallback if Alpine.js component is not accessible
    // Reset card button and hide processing indicator
    if (button) {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-lock mr-2"></i> Pay securely';
    }

    if (processingElement) {
        processingElement.classList.add('hidden');
    }
}

// Initialize payment methods when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Payment processing script loaded');

    // Wait for Alpine.js to initialize
    setTimeout(function() {
        // Get booking ID and amount from the page
        const bookingId = document.querySelector('[data-booking-id]')?.getAttribute('data-booking-id');
        const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');

        if (bookingId && bookingFormEl && bookingFormEl.__x) {
            const amount = bookingFormEl.__x.$data.totalPrice;
            const currencyCode = bookingFormEl.__x.$data.currencyCode;

            // Initialize PayPal buttons if PayPal SDK is loaded
            if (typeof paypal !== 'undefined') {
                initPayPalButtons(bookingId, amount, currencyCode);
            } else {
                // If PayPal SDK is not loaded, show a message
                const paypalButtonContainer = document.getElementById('paypal-button-container');
                if (paypalButtonContainer) {
                    paypalButtonContainer.innerHTML = `
                        <div class="bg-yellow-50 p-4 rounded-lg text-center text-yellow-700">
                            <i class="fas fa-exclamation-triangle mr-2"></i>
                            PayPal is not available at the moment. Please try again later or use a different payment method.
                        </div>
                    `;
                }
            }

            // Set up event listeners for payment buttons
            const paypalButton = document.querySelector('button[data-payment-method="paypal"]');
            const cardButton = document.querySelector('button[data-payment-method="card"]');
            const bankButton = document.querySelector('button[data-payment-method="bank"]');

            if (paypalButton) {
                paypalButton.addEventListener('click', function() {
                    processPayPalPayment(bookingId);
                });
            }

            if (cardButton) {
                cardButton.addEventListener('click', function() {
                    processCreditCardPayment(bookingId);
                });
            }

            if (bankButton) {
                bankButton.addEventListener('click', function() {
                    processBankTransfer(bookingId);
                });
            }
        } else {
            console.log('Booking form or booking ID not found');
        }
    }, 500); // Wait for Alpine.js to initialize
});

// Function to process PayPal payment (used by the PayPal button in the UI)
function processPayPalPayment(bookingId) {
    console.log('Processing PayPal payment for booking', bookingId);

    // Get the Alpine.js component instance
    const bookingFormEl = document.querySelector('[x-data="bookingConfirmation()"]');
    if (bookingFormEl && bookingFormEl.__x) {
        // Use the Alpine.js component's method
        bookingFormEl.__x.$data.processPayPalPayment(bookingId);
        return;
    }

    // Fallback if Alpine.js component is not accessible
    // Show processing state
    const paypalButton = document.querySelector('button[data-payment-method="paypal"]');
    const processingElement = document.getElementById('paypal-processing');

    if (paypalButton) {
        paypalButton.disabled = true;
        paypalButton.innerHTML = '<div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div> Processing...';
    }

    if (processingElement) {
        processingElement.classList.remove('hidden');
    }

    // Create PayPal order
    fetch(`/booking/${bookingId}/payment/paypal/create/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            throw new Error(data.error);
        }

        // Redirect to PayPal approval URL
        if (data.links && data.links.approve) {
            window.location.href = data.links.approve;
        } else {
            throw new Error('PayPal approval URL not found');
        }
    })
    .catch(function(error) {
        console.error('Error creating PayPal order:', error);
        showPaymentError(error.message || 'Failed to create PayPal order. Please try again or use a different payment method.');

        // Reset processing state
        if (paypalButton) {
            paypalButton.disabled = false;
            paypalButton.innerHTML = '<img src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/PP_logo_h_100x26.png" alt="PayPal" class="h-6 mr-2"> Pay with PayPal';
        }

        if (processingElement) {
            processingElement.classList.add('hidden');
        }
    });
}
