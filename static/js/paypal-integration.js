/**
 * PayPal Integration for Tourism Website
 * This script handles the PayPal integration for the booking process
 */

// Initialize PayPal integration
function initPayPal(bookingId, totalPrice, currencyCode) {
    console.log('Initializing PayPal integration for booking ID:', bookingId);
    console.log('Total price:', totalPrice, currencyCode);

    // Get the PayPal button container
    const paypalButtonContainer = document.getElementById('paypal-button-container');
    if (!paypalButtonContainer) {
        console.error('PayPal button container not found');
        return;
    }

    // Clear any existing content
    paypalButtonContainer.innerHTML = '';

    // Check if PayPal SDK is loaded
    if (typeof paypal === 'undefined') {
        console.error('PayPal SDK not loaded');
        
        // Show error message with fallback option
        paypalButtonContainer.innerHTML = `
            <div class="bg-blue-50 p-4 rounded-lg mb-4">
                <p class="text-blue-800 font-medium mb-2">PayPal SDK not loaded</p>
                <p class="text-blue-700 text-sm mb-3">The system is running in test mode. Click the button below to simulate a successful payment.</p>
                <button id="test-payment-button" class="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
                    <i class="fas fa-credit-card mr-2"></i> Simulate Successful Payment
                </button>
            </div>
        `;

        // Add event listener to the test button
        const testButton = document.getElementById('test-payment-button');
        if (testButton) {
            testButton.addEventListener('click', function() {
                console.log('Test payment button clicked');
                
                // Show loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
                this.disabled = true;
                
                // Simulate payment processing
                setTimeout(function() {
                    // Show success message
                    paypalButtonContainer.innerHTML = '<div class="text-center py-4 text-green-500"><i class="fas fa-check-circle text-2xl"></i><p class="mt-2 text-sm">Payment successful! Redirecting...</p></div>';
                    
                    // Move to confirmation step after a delay
                    setTimeout(function() {
                        // Get the Alpine.js component instance
                        const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
                        if (bookingFormEl && bookingFormEl.__x) {
                            // Access the Alpine.js component and update the currentStep
                            bookingFormEl.__x.$data.currentStep = 3;
                            
                            // Update confirmation details
                            updateConfirmationDetails(
                                'TEST-' + Math.floor(Math.random() * 10000),
                                bookingFormEl.__x.$data.startDate,
                                bookingFormEl.__x.$data.endDate,
                                bookingFormEl.__x.$data.numAdults,
                                bookingFormEl.__x.$data.numChildren,
                                totalPrice,
                                currencyCode
                            );
                            
                            // Scroll to top
                            window.scrollTo({top: 0, behavior: 'smooth'});
                        } else {
                            console.warn('Could not find Alpine.js component instance');
                            
                            // Fallback: try to show confirmation section directly
                            const confirmationSection = document.getElementById('confirmation-section');
                            if (confirmationSection) {
                                confirmationSection.style.display = 'block';
                                
                                // Hide other sections
                                const bookingSection = document.getElementById('booking-section');
                                const paymentSection = document.getElementById('payment-section');
                                
                                if (bookingSection) bookingSection.style.display = 'none';
                                if (paymentSection) paymentSection.style.display = 'none';
                                
                                // Scroll to top
                                window.scrollTo({top: 0, behavior: 'smooth'});
                            }
                        }
                    }, 1500);
                }, 2000);
            });
        }
        
        return;
    }

    // Initialize PayPal buttons
    paypal.Buttons({
        // Style the buttons
        style: {
            layout: 'vertical',  // vertical layout for better mobile experience
            color: 'blue',       // blue buttons
            shape: 'rect',       // rectangular shape
            label: 'paypal',     // Show PayPal logo to indicate multiple payment options
            height: 55,          // Larger height for better visibility
            tagline: false       // Remove tagline for cleaner look
        },
        
        // Set up the transaction
        createOrder: function(data, actions) {
            // Show loading indicator
            paypalButtonContainer.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i><p class="mt-2 text-sm text-gray-600">Connecting to PayPal...</p></div>';
            
            console.log('Creating PayPal order for booking ID:', bookingId);
            
            // For test mode, create a simulated order
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    // Clear the loading indicator
                    paypalButtonContainer.innerHTML = '';
                    
                    // Render the buttons again
                    paypal.Buttons({
                        style: {
                            layout: 'vertical',
                            color: 'blue',
                            shape: 'rect',
                            label: 'paypal',
                            height: 55,
                            tagline: false
                        }
                    }).render('#paypal-button-container');
                    
                    // Return a test order ID
                    resolve('TEST-ORDER-' + Math.floor(Math.random() * 1000000));
                }, 1500);
            });
        },
        
        // Finalize the transaction
        onApprove: function(data, actions) {
            // Show loading indicator
            paypalButtonContainer.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i><p class="mt-2 text-sm text-gray-600">Processing payment...</p></div>';
            
            console.log('Payment approved, order ID:', data.orderID);
            
            // Simulate payment processing
            setTimeout(function() {
                // Show success message
                paypalButtonContainer.innerHTML = '<div class="text-center py-4 text-green-500"><i class="fas fa-check-circle text-2xl"></i><p class="mt-2 text-sm">Payment successful! Redirecting...</p></div>';
                
                // Move to confirmation step after a delay
                setTimeout(function() {
                    // Get the Alpine.js component instance
                    const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
                    if (bookingFormEl && bookingFormEl.__x) {
                        // Access the Alpine.js component and update the currentStep
                        bookingFormEl.__x.$data.currentStep = 3;
                        
                        // Update confirmation details
                        updateConfirmationDetails(
                            data.orderID || ('TEST-' + Math.floor(Math.random() * 10000)),
                            bookingFormEl.__x.$data.startDate,
                            bookingFormEl.__x.$data.endDate,
                            bookingFormEl.__x.$data.numAdults,
                            bookingFormEl.__x.$data.numChildren,
                            totalPrice,
                            currencyCode
                        );
                        
                        // Scroll to top
                        window.scrollTo({top: 0, behavior: 'smooth'});
                    } else {
                        console.warn('Could not find Alpine.js component instance');
                        
                        // Fallback: try to show confirmation section directly
                        const confirmationSection = document.getElementById('confirmation-section');
                        if (confirmationSection) {
                            confirmationSection.style.display = 'block';
                            
                            // Hide other sections
                            const bookingSection = document.getElementById('booking-section');
                            const paymentSection = document.getElementById('payment-section');
                            
                            if (bookingSection) bookingSection.style.display = 'none';
                            if (paymentSection) paymentSection.style.display = 'none';
                            
                            // Scroll to top
                            window.scrollTo({top: 0, behavior: 'smooth'});
                        }
                    }
                }, 1500);
            }, 2000);
        },
        
        // Handle errors
        onError: function(err) {
            console.error('PayPal Error:', err);
            
            // Show user-friendly error message
            paypalButtonContainer.innerHTML = `
                <div class="bg-red-50 p-4 rounded-lg mb-4">
                    <p class="text-red-800 font-medium mb-2">Payment Error</p>
                    <p class="text-red-700 text-sm mb-3">There was an error processing your payment. Please try again or contact support.</p>
                    <button id="retry-button" class="px-4 py-2 bg-blue-600 text-white rounded-lg">Try Again</button>
                </div>
            `;
            
            // Add event listener to retry button
            const retryButton = document.getElementById('retry-button');
            if (retryButton) {
                retryButton.addEventListener('click', function() {
                    // Reinitialize PayPal
                    initPayPal(bookingId, totalPrice, currencyCode);
                });
            }
        },
        
        // Add onCancel handler
        onCancel: function() {
            console.log('Payment cancelled by user');
            
            paypalButtonContainer.innerHTML = `
                <div class="bg-yellow-50 p-4 rounded-lg mb-4">
                    <p class="text-yellow-800 font-medium mb-2">Payment Cancelled</p>
                    <p class="text-yellow-700 text-sm mb-3">You cancelled the payment process. You can try again when you're ready.</p>
                    <button id="retry-button" class="px-4 py-2 bg-blue-600 text-white rounded-lg">Try Again</button>
                </div>
            `;
            
            // Add event listener to retry button
            const retryButton = document.getElementById('retry-button');
            if (retryButton) {
                retryButton.addEventListener('click', function() {
                    // Reinitialize PayPal
                    initPayPal(bookingId, totalPrice, currencyCode);
                });
            }
        }
    }).render('#paypal-button-container');
}

// Initialize credit card payment
function initCreditCardPayment(bookingId, totalPrice, currencyCode) {
    console.log('Initializing credit card payment for booking ID:', bookingId);
    console.log('Total price:', totalPrice, currencyCode);
    
    // Get the card payment button
    const cardPaymentButton = document.getElementById('card-payment-button');
    if (!cardPaymentButton) {
        console.error('Card payment button not found');
        return;
    }
    
    // Remove any existing event listeners by cloning the button
    const newCardPaymentButton = cardPaymentButton.cloneNode(true);
    if (cardPaymentButton.parentNode) {
        cardPaymentButton.parentNode.replaceChild(newCardPaymentButton, cardPaymentButton);
    }
    
    // Update the button text to show the correct amount
    newCardPaymentButton.innerHTML = `<i class="fas fa-lock mr-2"></i> Pay Now (${totalPrice} ${currencyCode})`;
    
    // Add event listener to the new button
    newCardPaymentButton.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Card payment button clicked');
        
        // Show loading state
        const originalText = newCardPaymentButton.innerHTML;
        newCardPaymentButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
        newCardPaymentButton.disabled = true;
        
        // Simulate payment processing
        setTimeout(function() {
            try {
                // Get the card form container
                const cardFormContainer = document.getElementById('card-payment-form');
                if (cardFormContainer) {
                    cardFormContainer.innerHTML = `
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
                }
                
                // Move to confirmation step after a delay
                setTimeout(function() {
                    try {
                        // Get the Alpine.js component instance
                        const bookingFormEl = document.querySelector('[x-data="bookingForm()"]');
                        if (bookingFormEl && bookingFormEl.__x) {
                            // Access the Alpine.js component and update the currentStep
                            bookingFormEl.__x.$data.currentStep = 3;
                            
                            // Update confirmation details
                            updateConfirmationDetails(
                                'CARD-' + Math.floor(Math.random() * 10000),
                                bookingFormEl.__x.$data.startDate,
                                bookingFormEl.__x.$data.endDate,
                                bookingFormEl.__x.$data.numAdults,
                                bookingFormEl.__x.$data.numChildren,
                                totalPrice,
                                currencyCode
                            );
                            
                            // Force Alpine.js to update the UI
                            if (typeof Alpine !== 'undefined') {
                                Alpine.nextTick(() => {
                                    // Scroll to top
                                    window.scrollTo({top: 0, behavior: 'smooth'});
                                });
                            } else {
                                // Fallback if Alpine global is not available
                                window.scrollTo({top: 0, behavior: 'smooth'});
                            }
                        } else {
                            console.warn('Could not find Alpine.js component instance');
                            
                            // Fallback: try to show confirmation section directly
                            const confirmationSection = document.getElementById('confirmation-section');
                            if (confirmationSection) {
                                confirmationSection.style.display = 'block';
                                
                                // Hide other sections
                                const bookingSection = document.getElementById('booking-section');
                                const paymentSection = document.getElementById('payment-section');
                                
                                if (bookingSection) bookingSection.style.display = 'none';
                                if (paymentSection) paymentSection.style.display = 'none';
                                
                                // Scroll to top
                                window.scrollTo({top: 0, behavior: 'smooth'});
                            }
                        }
                    } catch (stepError) {
                        console.error('Error changing to confirmation step:', stepError);
                    }
                }, 1500);
            } catch (processError) {
                console.error('Error processing card payment:', processError);
                
                // Restore button state in case of error
                newCardPaymentButton.innerHTML = originalText;
                newCardPaymentButton.disabled = false;
            }
        }, 2000);
    });
}

// Function to update confirmation details
function updateConfirmationDetails(bookingId, startDate, endDate, numAdults, numChildren, totalPrice, currencyCode) {
    console.log('Updating confirmation details');
    
    // Set booking ID
    const bookingIdElement = document.getElementById('booking-id');
    if (bookingIdElement) {
        bookingIdElement.textContent = bookingId || 'TEST-123456';
    }
    
    // Set booking dates
    const bookingDatesElement = document.getElementById('booking-dates');
    if (bookingDatesElement) {
        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            bookingDatesElement.textContent = `${start.toLocaleDateString(undefined, options)} - ${end.toLocaleDateString(undefined, options)}`;
        } else {
            bookingDatesElement.textContent = 'Not specified';
        }
    }
    
    // Set booking participants
    const bookingParticipantsElement = document.getElementById('booking-participants');
    if (bookingParticipantsElement) {
        let participantsText = `${numAdults || 1} adults`;
        if (numChildren && numChildren > 0) {
            participantsText += `, ${numChildren} children`;
        }
        bookingParticipantsElement.textContent = participantsText;
    }
    
    // Set booking total
    const bookingTotalElement = document.getElementById('booking-total');
    if (bookingTotalElement) {
        bookingTotalElement.textContent = `${totalPrice || '0.00'} ${currencyCode || 'USD'}`;
    }
}
