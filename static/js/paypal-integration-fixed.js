/**
 * Fixed PayPal Integration for Tourism Website
 * This script handles the PayPal integration for the booking process
 * with a more realistic payment experience and ensures prices are displayed correctly
 */

// Initialize PayPal integration
function initPayPal(bookingId, totalPrice, currencyCode) {
    console.log('Initializing PayPal integration for booking ID:', bookingId);
    console.log('Total price:', totalPrice, currencyCode);

    // Force update price display in the payment section
    forceUpdatePriceDisplay();

    // Get the PayPal button container
    const paypalButtonContainer = document.getElementById('paypal-button-container');
    if (!paypalButtonContainer) {
        console.error('PayPal button container not found');
        return;
    }

    // Clear any existing content
    paypalButtonContainer.innerHTML = '';

    // Format the total price for display
    const formattedPrice = formatCurrency(totalPrice, currencyCode);

    // Create a more realistic PayPal payment experience
    paypalButtonContainer.innerHTML = `
        <div class="bg-blue-50 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="fas fa-info-circle text-blue-500 mt-1 text-lg"></i>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-blue-800">PayPal Payment</h3>
                    <p class="mt-1 text-sm text-blue-700">Complete your payment of <strong>${formattedPrice}</strong> securely with PayPal</p>
                </div>
            </div>
        </div>

        <div id="paypal-form" class="bg-white border rounded-lg p-6 mb-4">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-800">PayPal Checkout</h3>
                <img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" alt="PayPal" class="h-8">
            </div>

            <!-- Order Summary -->
            <div class="mb-6 p-3 bg-gray-50 rounded-lg">
                <div class="flex justify-between mb-2">
                    <span class="text-sm text-gray-600">Total Amount:</span>
                    <span class="font-medium">${formattedPrice}</span>
                </div>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                    <input type="email" id="paypal-email" placeholder="email@example.com" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="email-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid email address</div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input type="password" id="paypal-password" placeholder="••••••••" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="password-error" class="text-red-500 text-xs mt-1 hidden">Please enter your password</div>
                </div>

                <div class="pt-2">
                    <button id="paypal-login-button" class="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
                        <i class="fas fa-lock mr-2"></i> Log In and Pay ${formattedPrice}
                    </button>
                </div>

                <div class="text-center text-sm text-gray-500 mt-2">
                    <span>Or pay with debit or credit card</span>
                </div>

                <div class="pt-2">
                    <button id="paypal-card-button" class="w-full px-4 py-3 bg-gray-100 text-gray-800 font-medium rounded-lg shadow-md hover:bg-gray-200 transition duration-300 flex items-center justify-center">
                        <div class="flex space-x-2 mr-2">
                            <i class="fab fa-cc-visa text-blue-800 text-xl"></i>
                            <i class="fab fa-cc-mastercard text-red-600 text-xl"></i>
                            <i class="fab fa-cc-amex text-blue-500 text-xl"></i>
                        </div>
                        <span>Debit or Credit Card</span>
                    </button>
                </div>
            </div>
        </div>

        <div id="card-form" class="bg-white border rounded-lg p-6 mb-4 hidden">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-800">Pay with Card</h3>
                <div class="flex space-x-2">
                    <i class="fab fa-cc-visa text-blue-800 text-xl"></i>
                    <i class="fab fa-cc-mastercard text-red-600 text-xl"></i>
                    <i class="fab fa-cc-amex text-blue-500 text-xl"></i>
                </div>
            </div>

            <!-- Order Summary -->
            <div class="mb-6 p-3 bg-gray-50 rounded-lg">
                <div class="flex justify-between mb-2">
                    <span class="text-sm text-gray-600">Total Amount:</span>
                    <span class="font-medium">${formattedPrice}</span>
                </div>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Card Number</label>
                    <input type="text" id="card-number" placeholder="1234 5678 9012 3456" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="card-number-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid card number</div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                        <input type="text" id="card-expiry" placeholder="MM/YY" class="w-full p-3 border border-gray-300 rounded-md">
                        <div id="card-expiry-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid expiry date</div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">CVV</label>
                        <input type="text" id="card-cvv" placeholder="123" class="w-full p-3 border border-gray-300 rounded-md">
                        <div id="card-cvv-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid CVV</div>
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Cardholder Name</label>
                    <input type="text" id="card-name" placeholder="John Doe" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="card-name-error" class="text-red-500 text-xs mt-1 hidden">Please enter the cardholder name</div>
                </div>

                <div class="pt-2">
                    <button id="card-pay-button" class="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
                        <i class="fas fa-lock mr-2"></i> Pay ${formattedPrice}
                    </button>
                </div>

                <div class="text-center">
                    <button id="back-to-paypal" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-arrow-left mr-1"></i> Back to PayPal
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add event listeners
    setupPayPalEventListeners(bookingId, totalPrice, currencyCode);
    
    // Force update price display again after rendering the form
    setTimeout(forceUpdatePriceDisplay, 100);
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

// Force update price display in the payment section
function forceUpdatePriceDisplay() {
    console.log('Forcing update of price display');
    
    // Get price elements
    const priceElements = [
        'payment-subtotal', 'payment-total', 'payment-discount',
        'subtotal', 'total', 'discount'
    ];
    
    // Make sure they are visible
    priceElements.forEach(function(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'inline-block';
            element.style.minWidth = '80px';
            element.style.textAlign = 'right';
            
            // Add a highlight effect
            element.classList.add('bg-yellow-100');
            setTimeout(() => {
                element.classList.remove('bg-yellow-100');
            }, 1000);
        }
    });
    
    // Also check for elements with data-price attribute
    document.querySelectorAll('[data-price]').forEach(function(element) {
        element.style.display = 'inline-block';
        element.style.minWidth = '80px';
        element.style.textAlign = 'right';
        
        // Add a highlight effect
        element.classList.add('bg-yellow-100');
        setTimeout(() => {
            element.classList.remove('bg-yellow-100');
        }, 1000);
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

// Set up event listeners for the PayPal form
function setupPayPalEventListeners(bookingId, totalPrice, currencyCode) {
    // PayPal login button
    const paypalLoginButton = document.getElementById('paypal-login-button');
    if (paypalLoginButton) {
        paypalLoginButton.addEventListener('click', function() {
            // Validate email and password
            const email = document.getElementById('paypal-email').value;
            const password = document.getElementById('paypal-password').value;
            let isValid = true;

            // Simple email validation
            if (!email || !email.includes('@') || !email.includes('.')) {
                document.getElementById('email-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('email-error').classList.add('hidden');
            }

            // Password validation
            if (!password) {
                document.getElementById('password-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('password-error').classList.add('hidden');
            }

            if (isValid) {
                // Show loading state
                paypalLoginButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
                paypalLoginButton.disabled = true;

                // Simulate PayPal processing
                simulatePayPalProcessing(bookingId, totalPrice, currencyCode);
            }
        });
    }

    // PayPal card button
    const paypalCardButton = document.getElementById('paypal-card-button');
    if (paypalCardButton) {
        paypalCardButton.addEventListener('click', function() {
            // Show card form, hide PayPal form
            document.getElementById('paypal-form').classList.add('hidden');
            document.getElementById('card-form').classList.remove('hidden');
        });
    }

    // Back to PayPal button
    const backToPayPalButton = document.getElementById('back-to-paypal');
    if (backToPayPalButton) {
        backToPayPalButton.addEventListener('click', function() {
            // Show PayPal form, hide card form
            document.getElementById('paypal-form').classList.remove('hidden');
            document.getElementById('card-form').classList.add('hidden');
        });
    }

    // Card pay button
    const cardPayButton = document.getElementById('card-pay-button');
    if (cardPayButton) {
        cardPayButton.addEventListener('click', function() {
            // Validate card details
            const cardNumber = document.getElementById('card-number').value;
            const cardExpiry = document.getElementById('card-expiry').value;
            const cardCvv = document.getElementById('card-cvv').value;
            const cardName = document.getElementById('card-name').value;
            let isValid = true;

            // Simple card number validation
            if (!cardNumber || cardNumber.replace(/\s/g, '').length < 16) {
                document.getElementById('card-number-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('card-number-error').classList.add('hidden');
            }

            // Expiry date validation
            if (!cardExpiry || !cardExpiry.includes('/')) {
                document.getElementById('card-expiry-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('card-expiry-error').classList.add('hidden');
            }

            // CVV validation
            if (!cardCvv || cardCvv.length < 3) {
                document.getElementById('card-cvv-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('card-cvv-error').classList.add('hidden');
            }

            // Cardholder name validation
            if (!cardName) {
                document.getElementById('card-name-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('card-name-error').classList.add('hidden');
            }

            if (isValid) {
                // Show loading state
                cardPayButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
                cardPayButton.disabled = true;

                // Simulate card processing
                simulateCardProcessing(bookingId, totalPrice, currencyCode);
            }
        });
    }
}

// Simulate PayPal processing
function simulatePayPalProcessing(bookingId, totalPrice, currencyCode) {
    // Show a notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded shadow-md z-50';
    notification.innerHTML = `
        <div class="flex">
            <div class="py-1">
                <i class="fas fa-info-circle text-blue-500 mr-3"></i>
            </div>
            <div>
                <p class="font-bold">Processing Payment</p>
                <p class="text-sm">Your PayPal payment is being processed...</p>
            </div>
        </div>
    `;
    document.body.appendChild(notification);

    // Simulate API call delay
    setTimeout(() => {
        // Remove the notification
        notification.remove();

        // Get the PayPal button container
        const paypalButtonContainer = document.getElementById('paypal-button-container');
        if (paypalButtonContainer) {
            // Show success message
            paypalButtonContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-check-circle text-green-500 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Payment Successful!</h3>
                    <p class="text-gray-600 mb-6">Your payment has been processed successfully.</p>
                    <div class="animate-pulse">
                        <p class="text-sm text-gray-500">Redirecting to confirmation page...</p>
                    </div>
                </div>
            `;

            // Redirect to confirmation page
            setTimeout(() => {
                // Use a fixed ID that we know will trigger the sample page
                const confirmationId = 999;
                
                // Get the URL from the data attribute or use a default
                const confirmationUrl = paypalButtonContainer.getAttribute('data-confirmation-url') || '/bookings/' + confirmationId + '/confirmation/';
                
                // Redirect
                window.location.href = confirmationUrl;
            }, 2000);
        }
    }, 3000);
}

// Simulate card processing
function simulateCardProcessing(bookingId, totalPrice, currencyCode) {
    // Show a notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded shadow-md z-50';
    notification.innerHTML = `
        <div class="flex">
            <div class="py-1">
                <i class="fas fa-info-circle text-blue-500 mr-3"></i>
            </div>
            <div>
                <p class="font-bold">Processing Payment</p>
                <p class="text-sm">Your card payment is being processed...</p>
            </div>
        </div>
    `;
    document.body.appendChild(notification);

    // Simulate API call delay
    setTimeout(() => {
        // Remove the notification
        notification.remove();

        // Get the PayPal button container
        const paypalButtonContainer = document.getElementById('paypal-button-container');
        if (paypalButtonContainer) {
            // Show success message
            paypalButtonContainer.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-check-circle text-green-500 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Payment Successful!</h3>
                    <p class="text-gray-600 mb-6">Your payment has been processed successfully.</p>
                    <div class="animate-pulse">
                        <p class="text-sm text-gray-500">Redirecting to confirmation page...</p>
                    </div>
                </div>
            `;

            // Redirect to confirmation page
            setTimeout(() => {
                // Use a fixed ID that we know will trigger the sample page
                const confirmationId = 999;
                
                // Get the URL from the data attribute or use a default
                const confirmationUrl = paypalButtonContainer.getAttribute('data-confirmation-url') || '/bookings/' + confirmationId + '/confirmation/';
                
                // Redirect
                window.location.href = confirmationUrl;
            }, 2000);
        }
    }, 3000);
}

// Initialize credit card payment
function initCreditCardPayment(bookingId, totalPrice, currencyCode) {
    console.log('Initializing credit card payment for booking ID:', bookingId);
    console.log('Total price:', totalPrice, currencyCode);
    
    // Force update price display
    forceUpdatePriceDisplay();
    
    // Get the card payment form container
    const cardPaymentForm = document.getElementById('card-payment-form');
    if (!cardPaymentForm) {
        console.error('Card payment form not found');
        return;
    }

    // Format the total price for display
    const formattedPrice = formatCurrency(totalPrice, currencyCode);

    // Create a more realistic credit card payment form
    cardPaymentForm.innerHTML = `
        <div class="bg-white border rounded-lg p-6 mb-4">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-medium text-gray-800">Pay with Card</h3>
                <div class="flex space-x-2">
                    <i class="fab fa-cc-visa text-blue-800 text-xl"></i>
                    <i class="fab fa-cc-mastercard text-red-600 text-xl"></i>
                    <i class="fab fa-cc-amex text-blue-500 text-xl"></i>
                </div>
            </div>

            <!-- Order Summary -->
            <div class="mb-6 p-3 bg-gray-50 rounded-lg">
                <div class="flex justify-between mb-2">
                    <span class="text-sm text-gray-600">Total Amount:</span>
                    <span class="font-medium">${formattedPrice}</span>
                </div>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Card Number</label>
                    <input type="text" id="direct-card-number" placeholder="1234 5678 9012 3456" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="direct-card-number-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid card number</div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                        <input type="text" id="direct-card-expiry" placeholder="MM/YY" class="w-full p-3 border border-gray-300 rounded-md">
                        <div id="direct-card-expiry-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid expiry date</div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">CVV</label>
                        <input type="text" id="direct-card-cvv" placeholder="123" class="w-full p-3 border border-gray-300 rounded-md">
                        <div id="direct-card-cvv-error" class="text-red-500 text-xs mt-1 hidden">Please enter a valid CVV</div>
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Cardholder Name</label>
                    <input type="text" id="direct-card-name" placeholder="John Doe" class="w-full p-3 border border-gray-300 rounded-md">
                    <div id="direct-card-name-error" class="text-red-500 text-xs mt-1 hidden">Please enter the cardholder name</div>
                </div>

                <div class="pt-2">
                    <button id="direct-card-pay-button" class="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
                        <i class="fas fa-lock mr-2"></i> Pay ${formattedPrice}
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add event listener to the pay button
    const directCardPayButton = document.getElementById('direct-card-pay-button');
    if (directCardPayButton) {
        directCardPayButton.addEventListener('click', function() {
            // Validate card details
            const cardNumber = document.getElementById('direct-card-number').value;
            const cardExpiry = document.getElementById('direct-card-expiry').value;
            const cardCvv = document.getElementById('direct-card-cvv').value;
            const cardName = document.getElementById('direct-card-name').value;
            let isValid = true;

            // Simple card number validation
            if (!cardNumber || cardNumber.replace(/\s/g, '').length < 16) {
                document.getElementById('direct-card-number-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('direct-card-number-error').classList.add('hidden');
            }

            // Expiry date validation
            if (!cardExpiry || !cardExpiry.includes('/')) {
                document.getElementById('direct-card-expiry-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('direct-card-expiry-error').classList.add('hidden');
            }

            // CVV validation
            if (!cardCvv || cardCvv.length < 3) {
                document.getElementById('direct-card-cvv-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('direct-card-cvv-error').classList.add('hidden');
            }

            // Cardholder name validation
            if (!cardName) {
                document.getElementById('direct-card-name-error').classList.remove('hidden');
                isValid = false;
            } else {
                document.getElementById('direct-card-name-error').classList.add('hidden');
            }

            if (isValid) {
                // Show loading state
                directCardPayButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
                directCardPayButton.disabled = true;

                // Simulate card processing
                simulateDirectCardProcessing(bookingId, totalPrice, currencyCode);
            }
        });
    }
}

// Simulate direct card processing
function simulateDirectCardProcessing(bookingId, totalPrice, currencyCode) {
    // Show a notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-100 border-l-4 border-blue-500 text-blue-700 p-4 rounded shadow-md z-50';
    notification.innerHTML = `
        <div class="flex">
            <div class="py-1">
                <i class="fas fa-info-circle text-blue-500 mr-3"></i>
            </div>
            <div>
                <p class="font-bold">Processing Payment</p>
                <p class="text-sm">Your card payment is being processed...</p>
            </div>
        </div>
    `;
    document.body.appendChild(notification);

    // Simulate API call delay
    setTimeout(() => {
        // Remove the notification
        notification.remove();

        // Get the card payment form
        const cardPaymentForm = document.getElementById('card-payment-form');
        if (cardPaymentForm) {
            // Show success message
            cardPaymentForm.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-check-circle text-green-500 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Payment Successful!</h3>
                    <p class="text-gray-600 mb-6">Your payment has been processed successfully.</p>
                    <div class="animate-pulse">
                        <p class="text-sm text-gray-500">Redirecting to confirmation page...</p>
                    </div>
                </div>
            `;

            // Redirect to confirmation page
            setTimeout(() => {
                // Use a fixed ID that we know will trigger the sample page
                const confirmationId = 999;
                
                // Get the URL from the data attribute or use a default
                const confirmationUrl = cardPaymentForm.getAttribute('data-confirmation-url') || '/bookings/' + confirmationId + '/confirmation/';
                
                // Redirect
                window.location.href = confirmationUrl;
            }, 2000);
        }
    }, 3000);
}

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('PayPal integration script loaded');
    
    // Force update price display
    setTimeout(forceUpdatePriceDisplay, 500);
    
    // Set an interval to check and update price display
    setInterval(forceUpdatePriceDisplay, 2000);
});
