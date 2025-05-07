/**
 * Tour Filtering and Searching Functionality
 * Enhanced with auto-filtering
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const filterForm = document.getElementById('tour-filter-form');
    const searchInput = document.getElementById('search-input');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const durationSelect = document.getElementById('duration');
    const sortBySelect = document.getElementById('sort-by');
    const categorySelect = document.getElementById('category');
    const destinationSelect = document.getElementById('destination');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    const tourResults = document.getElementById('tour-results');
    const filterStatus = document.getElementById('filter-status');
    const filterStatusText = document.getElementById('filter-status-text');

    // Debounce function to prevent too many filter requests
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Price range slider (if using noUiSlider)
    const priceRangeSlider = document.getElementById('price-range-slider');

    // Initialize price range slider if it exists and noUiSlider is available
    if (priceRangeSlider && typeof noUiSlider !== 'undefined') {
        // Get min and max price from data attributes
        const minPrice = parseInt(priceRangeSlider.dataset.minPrice || 0);
        const maxPrice = parseInt(priceRangeSlider.dataset.maxPrice || 10000);
        const currentMinPrice = parseInt(minPriceInput.value || minPrice);
        const currentMaxPrice = parseInt(maxPriceInput.value || maxPrice);

        noUiSlider.create(priceRangeSlider, {
            start: [currentMinPrice, currentMaxPrice],
            connect: true,
            step: 10,
            range: {
                'min': minPrice,
                'max': maxPrice
            },
            format: {
                to: function(value) {
                    return Math.round(value);
                },
                from: function(value) {
                    return Math.round(value);
                }
            }
        });

        // Update input fields when slider changes
        priceRangeSlider.noUiSlider.on('update', function(values, handle) {
            if (handle === 0) {
                minPriceInput.value = values[0];
            } else {
                maxPriceInput.value = values[1];
            }

            // Update price display
            updatePriceDisplay(values[0], values[1]);
        });

        // Apply filters when slider stops being dragged
        priceRangeSlider.noUiSlider.on('change', debounce(function() {
            showFilterStatus('Updating price range...');
            applyFilters();
        }, 500));

        // Update slider when input fields change
        minPriceInput.addEventListener('change', function() {
            priceRangeSlider.noUiSlider.set([this.value, null]);
        });

        maxPriceInput.addEventListener('change', function() {
            priceRangeSlider.noUiSlider.set([null, this.value]);
        });
    }

    // Function to update price display
    function updatePriceDisplay(min, max) {
        const priceDisplay = document.getElementById('price-range-display');
        if (priceDisplay) {
            const currencySymbol = priceDisplay.dataset.currencySymbol || '$';
            priceDisplay.textContent = `${currencySymbol}${min} - ${currencySymbol}${max}`;
        }
    }

    // Function to show filter status
    function showFilterStatus(message) {
        if (filterStatus) {
            filterStatusText.textContent = message || 'Applying filters...';
            filterStatus.classList.remove('hidden');

            // Hide status after 2 seconds
            setTimeout(() => {
                filterStatus.classList.add('hidden');
            }, 2000);
        }
    }

    // Handle form submission (prevent default and use our custom handler)
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showFilterStatus();
            applyFilters();
        });
    }

    // Clear filters button
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showFilterStatus('Clearing filters...');
            clearFilters();
        });
    }

    // Add event listeners to all filter inputs for auto-filtering
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            showFilterStatus('Searching...');
            applyFilters();
        }, 500));
    }

    // Apply filters function
    function applyFilters() {
        if (filterStatus) {
            filterStatus.classList.remove('hidden');
        }

        // Get filter values
        const filters = {
            search: searchInput ? searchInput.value : '',
            min_price: minPriceInput ? minPriceInput.value : '',
            max_price: maxPriceInput ? maxPriceInput.value : '',
            duration: durationSelect ? durationSelect.value : '',
            sort: sortBySelect ? sortBySelect.value : '',
            category: categorySelect ? categorySelect.value : '',
            destination: destinationSelect ? destinationSelect.value : ''
        };

        // Build query string
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(filters)) {
            if (value) {
                queryParams.append(key, value);
            }
        }

        // Redirect to filtered results
        window.location.href = `${filterForm.action}?${queryParams.toString()}`;
    }

    // Clear filters function
    function clearFilters() {
        // Reset form inputs
        if (searchInput) searchInput.value = '';
        if (minPriceInput) minPriceInput.value = '';
        if (maxPriceInput) maxPriceInput.value = '';
        if (durationSelect) durationSelect.selectedIndex = 0;
        if (sortBySelect) sortBySelect.selectedIndex = 0;
        if (categorySelect) categorySelect.selectedIndex = 0;
        if (destinationSelect) destinationSelect.selectedIndex = 0;

        // Reset price range slider if it exists
        if (priceRangeSlider && priceRangeSlider.noUiSlider) {
            const minPrice = parseInt(priceRangeSlider.dataset.minPrice || 0);
            const maxPrice = parseInt(priceRangeSlider.dataset.maxPrice || 10000);
            priceRangeSlider.noUiSlider.set([minPrice, maxPrice]);
        }

        // Redirect to unfiltered results
        window.location.href = filterForm.action;
    }

    // Handle select element changes with visual feedback
    const selectElements = [
        { element: sortBySelect, message: 'Sorting tours...' },
        { element: durationSelect, message: 'Filtering by duration...' },
        { element: categorySelect, message: 'Filtering by category...' },
        { element: destinationSelect, message: 'Filtering by destination...' }
    ];

    selectElements.forEach(item => {
        if (item.element) {
            item.element.addEventListener('change', function() {
                showFilterStatus(item.message);
                applyFilters();
            });
        }
    });

    // Add a nice animation to select elements
    const allSelects = document.querySelectorAll('select');
    allSelects.forEach(select => {
        select.addEventListener('focus', function() {
            this.classList.add('ring-2', 'ring-blue-300');
        });

        select.addEventListener('blur', function() {
            this.classList.remove('ring-2', 'ring-blue-300');
        });
    });

    // Initialize any tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.dataset.tooltip;
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'tooltip absolute bg-gray-800 text-white text-xs rounded py-1 px-2 -mt-8 -ml-2 z-10';
            tooltipElement.textContent = tooltipText;
            this.appendChild(tooltipElement);
        });

        tooltip.addEventListener('mouseleave', function() {
            const tooltipElement = this.querySelector('.tooltip');
            if (tooltipElement) {
                tooltipElement.remove();
            }
        });
    });
});
