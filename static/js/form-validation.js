document.addEventListener('DOMContentLoaded', function() {
    console.log('Form validation script loaded');
    console.log('Debug mode enabled - check console for validation messages');

    // Get all forms with validation class
    const forms = document.querySelectorAll('form.needs-validation');

    forms.forEach(form => {
        console.log('Found form to validate:', form);

        // Get all input fields in the form
        const inputs = form.querySelectorAll('input[required]');
        const submitButton = form.querySelector('button[type="submit"]');

        // Keep submit button enabled
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
        }

        // Create an array to track field validation status
        const fieldStatus = {};

        // Initialize field status
        inputs.forEach(input => {
            const fieldName = input.name || input.id;
            fieldStatus[fieldName] = false;
            console.log('Tracking field:', fieldName);
        });

        // Function to validate email
        function validateEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) return false;

            const allowedDomains = ['com', 'net', 'org', 'edu', 'gov', 'io', 'co', 'info', 'biz', 'me'];
            const domain = email.split('@')[1].split('.').pop().toLowerCase();
            return allowedDomains.includes(domain);
        }

        // Function to validate password
        function validatePassword(password) {
            // At least 8 characters
            if (password.length < 8) return false;

            // At least one uppercase letter
            if (!/[A-Z]/.test(password)) return false;

            // At least one lowercase letter
            if (!/[a-z]/.test(password)) return false;

            // At least one number
            if (!/[0-9]/.test(password)) return false;

            // At least one special character
            const specialChars = ['@', '#', '%', '!', '$', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/'];
            if (!specialChars.some(char => password.includes(char))) return false;

            return true;
        }

        // Function to update feedback message
        function updateFeedback(input, isValid, message) {
            const fieldName = input.name || input.id;
            const feedbackId = fieldName.replace(/[\\[\\]]/g, '') + '-feedback';
            const feedbackElement = document.getElementById(feedbackId);

            if (feedbackElement) {
                feedbackElement.textContent = message;
                if (isValid) {
                    feedbackElement.classList.remove('text-red-600');
                    feedbackElement.classList.add('text-green-600');
                } else {
                    feedbackElement.classList.remove('text-green-600');
                    feedbackElement.classList.add('text-red-600');
                }
            }

            // Update field status
            fieldStatus[fieldName] = isValid;

            // Update submit button state
            updateSubmitButton();
        }

        // Function to update submit button state - always enabled
        function updateSubmitButton() {
            // Keep button always enabled, but we still track form validity
            const isFormValid = Object.values(fieldStatus).every(status => status === true);

            // For debugging purposes only
            console.log('Form valid:', isFormValid, 'Field status:', fieldStatus);
        }

        // Add validation to each input
        inputs.forEach(input => {
            // Validate on input
            input.addEventListener('input', function() {
                validateField(this);
            });

            // Validate on blur
            input.addEventListener('blur', function() {
                validateField(this);
            });

            // Still validate on tab but don't prevent tabbing
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Tab' && !e.shiftKey) {
                    validateField(this);
                    // Allow tabbing regardless of validation state
                }
            });
        });

        // Function to validate a field
        function validateField(input) {
            const fieldName = input.name || input.id;
            const value = input.value.trim();
            let isValid = false;
            let message = '';

            // Skip hidden fields
            if (input.type === 'hidden') {
                fieldStatus[fieldName] = true;
                return true;
            }

            // Validate based on field type
            if (input.type === 'email' || fieldName.includes('email') || fieldName.includes('login')) {
                isValid = validateEmail(value);
                message = isValid ? 'Email is valid' : 'Please enter a valid email with .com, .net, .org, etc.';
            } else if (input.type === 'password') {
                if (fieldName.includes('password2') || fieldName.includes('password_confirm')) {
                    // Confirm password field
                    const password1 = form.querySelector('input[name="password1"], input[name="password"]').value;
                    isValid = value === password1 && value !== '';
                    message = isValid ? 'Passwords match' : "Passwords don't match";
                } else {
                    // Password field
                    isValid = validatePassword(value);
                    message = isValid ? 'Password is valid' : 'Password must have 8+ chars with uppercase, lowercase, number, and special char';

                    // Update password feedback with detailed requirements
                    if (!isValid && fieldName.includes('password1')) {
                        const feedbackId = fieldName.replace(/[\\[\\]]/g, '') + '-feedback';
                        const feedbackElement = document.getElementById(feedbackId);

                        if (feedbackElement) {
                            // Create detailed feedback
                            let detailedFeedback = document.createElement('ul');
                            detailedFeedback.className = 'text-xs space-y-1 mt-1 list-disc pl-4';

                            // Check minimum length
                            let lengthItem = document.createElement('li');
                            lengthItem.textContent = 'At least 8 characters ' + (value.length >= 8 ? '✓' : '✗');
                            lengthItem.className = value.length >= 8 ? 'text-green-600' : 'text-red-600';
                            detailedFeedback.appendChild(lengthItem);

                            // Check for uppercase letter
                            let uppercaseItem = document.createElement('li');
                            uppercaseItem.textContent = 'Contains uppercase letter ' + (/[A-Z]/.test(value) ? '✓' : '✗');
                            uppercaseItem.className = /[A-Z]/.test(value) ? 'text-green-600' : 'text-red-600';
                            detailedFeedback.appendChild(uppercaseItem);

                            // Check for lowercase letter
                            let lowercaseItem = document.createElement('li');
                            lowercaseItem.textContent = 'Contains lowercase letter ' + (/[a-z]/.test(value) ? '✓' : '✗');
                            lowercaseItem.className = /[a-z]/.test(value) ? 'text-green-600' : 'text-red-600';
                            detailedFeedback.appendChild(lowercaseItem);

                            // Check for number
                            let numberItem = document.createElement('li');
                            numberItem.textContent = 'Contains number ' + (/[0-9]/.test(value) ? '✓' : '✗');
                            numberItem.className = /[0-9]/.test(value) ? 'text-green-600' : 'text-red-600';
                            detailedFeedback.appendChild(numberItem);

                            // Check for special character
                            const specialChars = ['@', '#', '%', '!', '$', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/'];
                            let specialCharItem = document.createElement('li');
                            specialCharItem.textContent = 'Contains special character ' + (specialChars.some(char => value.includes(char)) ? '✓' : '✗');
                            specialCharItem.className = specialChars.some(char => value.includes(char)) ? 'text-green-600' : 'text-red-600';
                            detailedFeedback.appendChild(specialCharItem);

                            // Clear previous feedback and add new detailed feedback
                            feedbackElement.innerHTML = '';
                            feedbackElement.appendChild(detailedFeedback);
                        }
                    }
                }
            } else if (fieldName.includes('first_name') || fieldName.includes('last_name')) {
                isValid = value.length > 0;
                message = isValid ? fieldName.includes('first_name') ? 'First name is valid' : 'Last name is valid' : 'This field is required';
            } else if (input.type === 'checkbox') {
                isValid = input.checked;
                message = isValid ? 'Accepted' : 'Please accept the terms';
            } else {
                // Default validation for other fields
                isValid = value.length > 0;
                message = isValid ? 'Valid' : 'This field is required';
            }

            // Update feedback
            updateFeedback(input, isValid, message);

            return isValid;
        }

        // Handle form submission - allow submission even with invalid fields
        form.addEventListener('submit', function(e) {
            // Validate all fields but don't prevent submission
            inputs.forEach(input => {
                validateField(input);
            });

            // Log validation status for debugging
            const isFormValid = Object.values(fieldStatus).every(status => status === true);
            console.log('Form submitted. Valid:', isFormValid);

            // Allow form submission regardless of validation state
        });
    });
});
