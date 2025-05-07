document.addEventListener('DOMContentLoaded', function () {
    // Initialize Swiper for the tour gallery with a short delay to ensure all resources are loaded
    setTimeout(initializeSwiper, 100);
    
    function initializeSwiper() {
        if (typeof Swiper !== 'undefined') {
            const swiperContainer = document.querySelector('.tourGallerySwiper');
            if (swiperContainer) {
                console.log('Initializing Swiper for .tourGallerySwiper');
                try {
                    const tourGallerySwiper = new Swiper(swiperContainer, {
                        loop: true,
                        spaceBetween: 10,
                        navigation: {
                            nextEl: '.swiper-button-next',
                            prevEl: '.swiper-button-prev',
                        },
                        pagination: {
                            el: '.swiper-pagination',
                            clickable: true,
                        },
                        keyboard: {
                            enabled: true,
                        },
                        // Added additional configuration
                        effect: 'slide',
                        speed: 600,
                        slidesPerView: 1,
                        autoplay: {
                            delay: 5000,
                            disableOnInteraction: false,
                        },
                        lazy: true,
                        preloadImages: false,
                        direction: 'horizontal',
                    });
                    console.log('Swiper initialized successfully.');
                } catch (error) {
                    console.error('Error initializing Swiper:', error);
                }
            } else {
                console.error('Swiper container (.tourGallerySwiper) not found.');
            }
        } else {
            console.error('Swiper library not loaded. Please check if the Swiper script is being properly loaded.');
            // Try again after a delay
            setTimeout(initializeSwiper, 500);
        }
    }

    // Initialize Flatpickr for the tour date selection
    const datePickerInput = document.getElementById('tour-date-picker');
    const hiddenDateInput = document.getElementById('tour_date_id');
    const availableDatesDataElement = document.getElementById('available-dates-data');

    if (datePickerInput && hiddenDateInput && availableDatesDataElement && typeof flatpickr !== 'undefined') {
        console.log('Initializing Flatpickr for #tour-date-picker');
        try {
            const availableDatesData = JSON.parse(availableDatesDataElement.textContent);
            const enabledDates = availableDatesData.map(item => item.date); // Extract YYYY-MM-DD strings
            const dateMap = {}; // Map YYYY-MM-DD to TourDate ID
            availableDatesData.forEach(item => {
                dateMap[item.date] = item.id;
            });

            flatpickr(datePickerInput, {
                dateFormat: "Y-m-d", // Set the format displayed in the input
                altInput: true, // Show a more human-friendly format
                altFormat: "F j, Y", // Format displayed to the user (e.g., April 6, 2025)
                minDate: "today", // Don't allow past dates
                enable: enabledDates, // Only allow selection of specific available dates
                onChange: function(selectedDates, dateStr, instance) {
                    // When a date is selected, find the corresponding TourDate ID
                    const selectedDateStr = instance.formatDate(selectedDates[0], "Y-m-d");
                    const tourDateId = dateMap[selectedDateStr];
                    
                    if (tourDateId) {
                        hiddenDateInput.value = tourDateId; // Update the hidden input value
                        console.log(`Selected date: ${dateStr}, TourDate ID: ${tourDateId}`);
                    } else {
                        hiddenDateInput.value = ""; // Clear if somehow an invalid date was selected
                        console.error(`Could not find TourDate ID for selected date: ${dateStr}`);
                    }
                },
                onClose: function(selectedDates, dateStr, instance) {
                    // Clear hidden input if no date is selected when closing
                    if (selectedDates.length === 0) {
                        hiddenDateInput.value = "";
                    }
                }
            });
            console.log('Flatpickr initialized successfully.');

        } catch (e) {
            console.error('Error parsing available dates JSON or initializing Flatpickr:', e);
        }
    } else {
        if (!datePickerInput) console.error('Flatpickr target input (#tour-date-picker) not found.');
        if (!hiddenDateInput) console.error('Hidden date input (#tour_date_id) not found.');
        if (!availableDatesDataElement) console.error('Available dates data script element (#available-dates-data) not found.');
        if (typeof flatpickr === 'undefined') console.error('Flatpickr library not loaded or available.');
    }
});

// Also initialize on window load to ensure all assets are loaded
window.addEventListener('load', function() {
    if (typeof Swiper !== 'undefined') {
        const swiperContainer = document.querySelector('.tourGallerySwiper');
        if (swiperContainer) {
            console.log('Reinitializing Swiper on window.load');
            try {
                const tourGallerySwiper = new Swiper(swiperContainer, {
                    loop: true,
                    spaceBetween: 10,
                    navigation: {
                        nextEl: '.swiper-button-next',
                        prevEl: '.swiper-button-prev',
                    },
                    pagination: {
                        el: '.swiper-pagination',
                        clickable: true,
                    },
                    keyboard: {
                        enabled: true,
                    },
                    // Added additional configuration
                    effect: 'slide',
                    speed: 600,
                    slidesPerView: 1,
                    autoplay: {
                        delay: 5000,
                        disableOnInteraction: false,
                    },
                    lazy: true,
                    preloadImages: false,
                    direction: 'horizontal',
                });
                console.log('Swiper reinitialized successfully on window.load.');
            } catch (error) {
                console.error('Error reinitializing Swiper on window.load:', error);
            }
        }
    }
});