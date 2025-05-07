/**
 * Tour Reviews System
 * Handles star rating, review submission, and review statistics visualization
 */
document.addEventListener('DOMContentLoaded', function() {
    // Star rating system for review form
    initStarRating();

    // Initialize review charts
    initReviewCharts();

    // Handle review form submission
    initReviewForm();

    // Initialize review filtering
    initReviewFiltering();
});

/**
 * Initialize star rating system
 */
function initStarRating() {
    console.log('Initializing star rating system');

    // Get the rating container
    const ratingContainer = document.getElementById('review-rating-stars');
    if (!ratingContainer) {
        console.log('Rating container not found');
        return;
    }

    // Get all star labels and radio inputs
    const stars = ratingContainer.querySelectorAll('.star-label');
    const inputs = ratingContainer.querySelectorAll('input[type="radio"]');

    console.log(`Found ${stars.length} stars and ${inputs.length} inputs`);

    // Clear any existing event listeners
    const newContainer = ratingContainer.cloneNode(true);
    ratingContainer.parentNode.replaceChild(newContainer, ratingContainer);

    // Get fresh references after replacement
    const freshContainer = document.getElementById('review-rating-stars');
    const freshStars = freshContainer.querySelectorAll('.star-label');
    const freshInputs = freshContainer.querySelectorAll('input[type="radio"]');

    console.log(`After refresh: ${freshStars.length} stars and ${freshInputs.length} inputs`);

    // Function to update star colors
    function updateStars(activeIndex) {
        console.log(`Updating stars with active index: ${activeIndex}`);

        // Make sure we're working with a valid index
        if (activeIndex < 0) activeIndex = -1;
        if (activeIndex >= freshStars.length) activeIndex = freshStars.length - 1;

        // Update each star's color
        freshStars.forEach((star, i) => {
            if (i <= activeIndex) {
                // This star and all previous ones should be highlighted
                star.classList.add('text-yellow-400');
                star.classList.remove('text-gray-300');
            } else {
                // Stars after the active index should be gray
                star.classList.remove('text-yellow-400');
                star.classList.add('text-gray-300');
            }
        });
    }

    // Convert NodeList to Array for easier manipulation
    const starsArray = Array.from(freshStars);
    const inputsArray = Array.from(freshInputs);

    // Function to get the currently selected rating
    function getSelectedRating() {
        for (let i = 0; i < inputsArray.length; i++) {
            if (inputsArray[i].checked) {
                return i;
            }
        }
        return -1;
    }

    // Add hover events to stars
    starsArray.forEach((star, index) => {
        // On hover, highlight this star and all previous ones
        star.addEventListener('mouseenter', () => {
            console.log(`Mouse entered star ${index + 1}`);
            updateStars(index);
        });

        // On click, set the rating
        star.addEventListener('click', (e) => {
            console.log(`Clicked star ${index + 1}`);
            e.preventDefault(); // Prevent default label behavior

            // Uncheck all inputs first
            inputsArray.forEach(input => {
                input.checked = false;
            });

            // Check only the selected input
            inputsArray[index].checked = true;

            // Update stars
            updateStars(index);
        });
    });

    // When mouse leaves the container, reset to selected rating
    freshContainer.addEventListener('mouseleave', () => {
        console.log('Mouse left container');
        const selectedIndex = getSelectedRating();
        updateStars(selectedIndex);
    });

    // Handle keyboard navigation
    inputsArray.forEach((input, index) => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' && index > 0) {
                // Left arrow - decrease rating
                inputsArray[index - 1].checked = true;
                updateStars(index - 1);
            } else if (e.key === 'ArrowRight' && index < inputsArray.length - 1) {
                // Right arrow - increase rating
                inputsArray[index + 1].checked = true;
                updateStars(index + 1);
            }
        });
    });

    // Initialize with any pre-selected rating
    const initialRating = getSelectedRating();
    if (initialRating >= 0) {
        updateStars(initialRating);
    }

    console.log('Star rating initialization complete');
}

/**
 * Initialize review charts using Chart.js
 */
function initReviewCharts() {
    console.log('Initializing review charts...');
    // Rating distribution chart
    const ratingChartCanvas = document.getElementById('rating-distribution-chart');
    if (!ratingChartCanvas) {
        console.error('Rating chart canvas not found');
        return;
    }

    // Get rating data from data attributes
    const ratingData = [];
    const ratingLabels = [];
    const ratingCounts = [];

    // Debug data attributes
    console.log('Chart canvas data attributes:');
    for (let i = 5; i >= 1; i--) {
        console.log(`data-rating-${i}:`, ratingChartCanvas.getAttribute(`data-rating-${i}`));
        console.log(`data-count-${i}:`, ratingChartCanvas.getAttribute(`data-count-${i}`));

        const percentage = parseInt(ratingChartCanvas.getAttribute(`data-rating-${i}`)) || 0;
        ratingLabels.push(`${i} ${i === 1 ? 'Star' : 'Stars'}`);
        ratingData.push(percentage);
        ratingCounts.push(parseInt(ratingChartCanvas.getAttribute(`data-count-${i}`)) || 0);
    }

    console.log('Rating data:', ratingData);
    console.log('Rating labels:', ratingLabels);
    console.log('Rating counts:', ratingCounts);

    // Create horizontal bar chart
    if (typeof Chart !== 'undefined') {
        console.log('Chart.js is loaded, creating chart...');
        try {
            new Chart(ratingChartCanvas, {
                type: 'bar',
                data: {
                    labels: ratingLabels,
                    datasets: [{
                        label: 'Rating Distribution',
                        data: ratingData,
                        backgroundColor: [
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(255, 193, 7, 0.6)',
                            'rgba(255, 193, 7, 0.5)',
                            'rgba(255, 193, 7, 0.4)',
                            'rgba(255, 193, 7, 0.3)'
                        ],
                        borderColor: [
                            'rgba(255, 193, 7, 1)',
                            'rgba(255, 193, 7, 1)',
                            'rgba(255, 193, 7, 1)',
                            'rgba(255, 193, 7, 1)',
                            'rgba(255, 193, 7, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const index = context.dataIndex;
                                    return `${ratingData[index]}% (${ratingCounts[index]} reviews)`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
            console.log('Chart created successfully');
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    } else {
        console.error('Chart.js is not loaded');
    }

    // Update rating progress bars
    updateRatingProgressBars();
}

/**
 * Update rating progress bars
 */
function updateRatingProgressBars() {
    const progressBars = document.querySelectorAll('.rating-progress-bar');

    progressBars.forEach(bar => {
        const percentage = parseInt(bar.getAttribute('data-percentage')) || 0;
        bar.style.width = `${percentage}%`;
    });
}

/**
 * Initialize review form submission
 */
function initReviewForm() {
    const reviewForm = document.getElementById('review-form');
    if (!reviewForm) return;

    reviewForm.addEventListener('submit', function(e) {
        const ratingInputs = document.querySelectorAll('input[name="rating"]');
        const commentInput = document.getElementById('comment');

        let isValid = true;
        let ratingSelected = false;

        // Check if rating is selected
        ratingInputs.forEach(input => {
            if (input.checked) {
                ratingSelected = true;
            }
        });

        if (!ratingSelected) {
            isValid = false;
            showError('Please select a rating');
        }

        // Check if comment is entered
        if (!commentInput.value.trim()) {
            isValid = false;
            showError('Please enter a comment');
        }

        if (!isValid) {
            e.preventDefault();
        }
    });
}

/**
 * Show error message
 */
function showError(message) {
    const errorContainer = document.getElementById('review-form-errors');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');

        // Hide error after 3 seconds
        setTimeout(() => {
            errorContainer.classList.add('hidden');
        }, 3000);
    } else {
        alert(message);
    }
}

/**
 * Initialize review filtering
 */
function initReviewFiltering() {
    console.log('Initializing review filtering...');
    const filterButtons = document.querySelectorAll('.review-filter-btn');
    if (!filterButtons.length) {
        console.error('No filter buttons found');
        return;
    }

    console.log('Found filter buttons:', filterButtons.length);

    filterButtons.forEach(button => {
        const filter = button.getAttribute('data-filter');
        console.log('Filter button:', filter);

        button.addEventListener('click', function() {
            console.log('Filter button clicked:', filter);

            // Remove active class from all buttons
            filterButtons.forEach(btn => {
                btn.classList.remove('bg-blue-600', 'text-white');
                btn.classList.add('bg-gray-200', 'text-gray-700');
            });

            // Add active class to clicked button
            this.classList.remove('bg-gray-200', 'text-gray-700');
            this.classList.add('bg-blue-600', 'text-white');

            // Filter reviews
            filterReviews(filter);
        });
    });
}

/**
 * Filter reviews based on rating
 */
function filterReviews(filter) {
    console.log('Filtering reviews by:', filter);
    const reviews = document.querySelectorAll('.review-item');
    if (!reviews.length) {
        console.error('No review items found');
        return;
    }

    console.log('Found review items:', reviews.length);

    let visibleCount = 0;

    reviews.forEach(review => {
        const rating = parseInt(review.getAttribute('data-rating')) || 0;
        console.log('Review rating:', rating);

        let shouldShow = false;

        if (filter === 'all') {
            shouldShow = true;
        } else if (filter === 'positive' && rating >= 4) {
            shouldShow = true;
        } else if (filter === 'neutral' && rating === 3) {
            shouldShow = true;
        } else if (filter === 'negative' && rating <= 2) {
            shouldShow = true;
        }

        if (shouldShow) {
            review.classList.remove('hidden');
            visibleCount++;
        } else {
            review.classList.add('hidden');
        }
    });

    console.log('Visible reviews after filtering:', visibleCount);

    // Show message if no reviews match filter
    const noReviewsMessage = document.getElementById('no-filtered-reviews');
    if (noReviewsMessage) {
        if (visibleCount === 0) {
            console.log('No reviews match the filter, showing message');
            noReviewsMessage.classList.remove('hidden');
        } else {
            noReviewsMessage.classList.add('hidden');
        }
    } else {
        console.error('No filtered reviews message element found');
    }
}
