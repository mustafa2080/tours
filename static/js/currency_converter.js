/**
 * Currency conversion functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Cache for exchange rates
    let exchangeRates = {};
    let currentCurrency = document.querySelector('meta[name="current-currency"]')?.content || 'USD';
    
    // Fetch exchange rates from the server
    function fetchExchangeRates() {
        fetch('/api/exchange-rates/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching exchange rates:', data.error);
                    return;
                }
                
                exchangeRates = data.rates;
                updateAllPrices();
            })
            .catch(error => {
                console.error('Failed to fetch exchange rates:', error);
            });
    }
    
    // Update all prices on the page
    function updateAllPrices() {
        const priceElements = document.querySelectorAll('[data-price-usd]');
        
        priceElements.forEach(element => {
            const basePrice = parseFloat(element.getAttribute('data-price-usd'));
            if (isNaN(basePrice)) return;
            
            const rate = exchangeRates[currentCurrency]?.rate || 1;
            const symbol = exchangeRates[currentCurrency]?.symbol || '$';
            
            const convertedPrice = (basePrice * rate).toFixed(2);
            element.textContent = `${symbol}${convertedPrice}`;
        });
    }
    
    // Handle currency selection change
    const currencySelector = document.getElementById('currency-selector');
    if (currencySelector) {
        currencySelector.addEventListener('change', function(e) {
            const form = e.target.closest('form');
            
            // Update UI immediately before form submission
            currentCurrency = e.target.value;
            updateAllPrices();
            
            // Submit the form to update the session
            form.submit();
        });
    }
    
    // Initial fetch of exchange rates
    fetchExchangeRates();
});