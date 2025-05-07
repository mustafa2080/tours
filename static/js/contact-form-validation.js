/**
 * Contact Form Validation
 * Beautiful real-time validation for the contact form
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const contactForm = document.getElementById('contact-form');
    if (!contactForm) return;

    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const subjectInput = document.getElementById('subject');
    const messageInput = document.getElementById('message');
    const submitButton = contactForm.querySelector('button[type="submit"]');

    // Validation state object
    const validationState = {
        name: false,
        email: false,
        subject: false,
        message: false
    };

    // Create validation feedback elements for each field
    function createFeedbackElements(input, fieldName) {
        // Create feedback container if it doesn't exist
        let feedbackContainer = document.getElementById(`${fieldName}-feedback`);
        if (!feedbackContainer) {
            feedbackContainer = document.createElement('div');
            feedbackContainer.id = `${fieldName}-feedback`;
            feedbackContainer.className = 'mt-1 text-sm hidden';
            input.parentNode.appendChild(feedbackContainer);
        }

        // Create validation icon container if it doesn't exist
        let validationIcon = input.parentNode.querySelector('.validation-icon');
        if (!validationIcon) {
            validationIcon = document.createElement('div');
            validationIcon.className = 'absolute inset-y-0 right-0 pr-3 flex items-center validation-icon hidden';

            // Add success and error icons
            validationIcon.innerHTML = `
                <svg class="success-icon hidden h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg class="error-icon hidden h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
            `;

            input.parentNode.appendChild(validationIcon);
        }

        return { feedbackContainer, validationIcon };
    }

    // Initialize feedback elements for all fields
    const nameElements = createFeedbackElements(nameInput, 'name');
    const emailElements = createFeedbackElements(emailInput, 'email');
    const subjectElements = createFeedbackElements(subjectInput, 'subject');
    const messageElements = createFeedbackElements(messageInput, 'message');

    // Validation functions
    function validateName() {
        const name = nameInput.value.trim();
        const isValid = name.length >= 2;

        updateValidationUI(
            nameInput,
            nameElements.feedbackContainer,
            nameElements.validationIcon,
            isValid,
            isValid ? 'Name looks good!' : 'Please enter your name (at least 2 characters)'
        );

        validationState.name = isValid;
        updateSubmitButton();
        return isValid;
    }

    function validateEmail() {
        const email = emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);

        updateValidationUI(
            emailInput,
            emailElements.feedbackContainer,
            emailElements.validationIcon,
            isValid,
            isValid ? 'Email looks good!' : 'Please enter a valid email address'
        );

        validationState.email = isValid;
        updateSubmitButton();
        return isValid;
    }

    function validateSubject() {
        const subject = subjectInput.value.trim();
        const isValid = subject.length >= 3;

        updateValidationUI(
            subjectInput,
            subjectElements.feedbackContainer,
            subjectElements.validationIcon,
            isValid,
            isValid ? 'Subject looks good!' : 'Please enter a subject (at least 3 characters)'
        );

        validationState.subject = isValid;
        updateSubmitButton();
        return isValid;
    }

    function validateMessage() {
        const message = messageInput.value.trim();
        const isValid = message.length >= 10;

        updateValidationUI(
            messageInput,
            messageElements.feedbackContainer,
            messageElements.validationIcon,
            isValid,
            isValid ? 'Message looks good!' : 'Please enter a message (at least 10 characters)'
        );

        validationState.message = isValid;
        updateSubmitButton();
        return isValid;
    }

    // Update validation UI
    function updateValidationUI(input, feedbackContainer, validationIcon, isValid, message) {
        // Update input styling
        if (isValid) {
            input.classList.remove('border-red-300', 'focus:ring-red-500', 'focus:border-red-500');
            input.classList.add('border-green-300', 'focus:ring-green-500', 'focus:border-green-500');
        } else {
            input.classList.remove('border-green-300', 'focus:ring-green-500', 'focus:border-green-500');
            input.classList.add('border-red-300', 'focus:ring-red-500', 'focus:border-red-500');
        }

        // Update feedback message
        feedbackContainer.textContent = message;
        feedbackContainer.classList.remove('hidden', 'text-green-600', 'text-red-600');
        feedbackContainer.classList.add(isValid ? 'text-green-600' : 'text-red-600');

        // Update validation icon
        validationIcon.classList.remove('hidden');
        const successIcon = validationIcon.querySelector('.success-icon');
        const errorIcon = validationIcon.querySelector('.error-icon');

        if (isValid) {
            successIcon.classList.remove('hidden');
            errorIcon.classList.add('hidden');
        } else {
            successIcon.classList.add('hidden');
            errorIcon.classList.remove('hidden');
        }
    }

    // Update submit button state
    function updateSubmitButton() {
        const isFormValid = Object.values(validationState).every(value => value === true);

        if (isFormValid) {
            submitButton.classList.remove('opacity-70', 'cursor-not-allowed');
            submitButton.classList.add('hover:bg-primary-dark', 'transform', 'hover:scale-105');
        } else {
            submitButton.classList.add('opacity-70', 'cursor-not-allowed');
            submitButton.classList.remove('hover:bg-primary-dark', 'transform', 'hover:scale-105');
        }

        // Don't disable the button to allow server-side validation
        // submitButton.disabled = !isFormValid;
    }

    // Add event listeners
    nameInput.addEventListener('input', debounce(validateName, 300));
    nameInput.addEventListener('blur', validateName);

    emailInput.addEventListener('input', debounce(validateEmail, 300));
    emailInput.addEventListener('blur', validateEmail);

    subjectInput.addEventListener('input', debounce(validateSubject, 300));
    subjectInput.addEventListener('blur', validateSubject);

    messageInput.addEventListener('input', debounce(validateMessage, 300));
    messageInput.addEventListener('blur', validateMessage);

    // Form submission
    contactForm.addEventListener('submit', function(e) {
        // Validate all fields
        const isNameValid = validateName();
        const isEmailValid = validateEmail();
        const isSubjectValid = validateSubject();
        const isMessageValid = validateMessage();

        // Get form status elements
        const formStatus = document.getElementById('form-status');
        const formSuccess = document.getElementById('form-success');
        const formError = document.getElementById('form-error');

        // If any field is invalid, prevent form submission
        if (!(isNameValid && isEmailValid && isSubjectValid && isMessageValid)) {
            e.preventDefault();

            // Show error message
            formStatus.classList.remove('hidden');
            formSuccess.classList.add('hidden');
            formError.classList.remove('hidden');

            // Add shake animation to error message
            formError.classList.add('animate-shake');
            setTimeout(() => {
                formError.classList.remove('animate-shake');
            }, 500);

            // Scroll to the first invalid field
            const firstInvalidField = [nameInput, emailInput, subjectInput, messageInput].find(input => {
                const fieldName = input.id;
                return !validationState[fieldName];
            });

            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            // All fields are valid, allow form submission
            // Add loading state to button
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Sending...';
            submitButton.disabled = true;
            submitButton.classList.add('opacity-70', 'cursor-not-allowed');

            // We'll let the server handle the actual submission
        }
    });

    // Debounce function to limit how often a function can be called
    function debounce(func, delay) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    }
});
