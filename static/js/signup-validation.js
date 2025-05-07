document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.querySelector('form');
    const emailInput = document.querySelector('input[type="email"]');
    const password1Input = document.querySelector('input[name="password1"]');
    const password2Input = document.querySelector('input[name="password2"]');
    const firstNameInput = document.querySelector('input[name="first_name"]');
    const lastNameInput = document.querySelector('input[name="last_name"]');
    const signupButton = document.querySelector('button[type="submit"]');

    // Track validation state
    const validationState = {
        email: false,
        password1: false,
        password2: false,
        first_name: false,
        last_name: false
    };

    // Email validation
    function validateEmail() {
        const email = emailInput.value.trim();
        const formGroup = emailInput.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById('email-feedback');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        formGroup.classList.remove('is-valid', 'is-invalid');
        validationIcon.classList.remove('hidden');

        if (!email) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Email is required';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.email = false;
        } else if (!emailRegex.test(email)) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Please enter a valid email address';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.email = false;
        } else {
            formGroup.classList.add('is-valid');
            feedback.textContent = 'Email is valid';
            feedback.className = 'mt-1 text-sm text-green-600';
            validationState.email = true;
        }

        updateSubmitButton();
    }

    // Password validation with strength indicator
    function validatePassword1() {
        const password = password1Input.value;
        const formGroup = password1Input.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById('password1-feedback');

        // Create or get password strength meter
        let strengthMeter = document.querySelector('.password-strength-meter');
        if (!strengthMeter) {
            strengthMeter = document.createElement('div');
            strengthMeter.className = 'password-strength-meter';
            strengthMeter.innerHTML = '<div></div>';
            feedback.parentNode.insertBefore(strengthMeter, feedback);
        }
        const strengthBar = strengthMeter.querySelector('div');

        formGroup.classList.remove('is-valid', 'is-invalid');
        validationIcon.classList.remove('hidden');

        // Password strength criteria
        const hasLength = password.length >= 8;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        const strengthChecks = [hasLength, hasUpper, hasLower, hasNumber, hasSpecial];
        const passedChecks = strengthChecks.filter(check => check).length;

        // Update feedback with detailed requirements
        let detailedFeedback = '<ul class="text-xs space-y-1 mt-1">';
        detailedFeedback += '<li class="' + (hasLength ? 'text-green-600' : 'text-red-600') + '">At least 8 characters ' + (hasLength ? '✓' : '✗') + '</li>';
        detailedFeedback += '<li class="' + (hasUpper ? 'text-green-600' : 'text-red-600') + '">Uppercase letter ' + (hasUpper ? '✓' : '✗') + '</li>';
        detailedFeedback += '<li class="' + (hasLower ? 'text-green-600' : 'text-red-600') + '">Lowercase letter ' + (hasLower ? '✓' : '✗') + '</li>';
        detailedFeedback += '<li class="' + (hasNumber ? 'text-green-600' : 'text-red-600') + '">Number ' + (hasNumber ? '✓' : '✗') + '</li>';
        detailedFeedback += '<li class="' + (hasSpecial ? 'text-green-600' : 'text-red-600') + '">Special character ' + (hasSpecial ? '✓' : '✗') + '</li>';
        detailedFeedback += '</ul>';

        feedback.innerHTML = detailedFeedback;

        // Update strength meter
        let strengthPercentage = (passedChecks / strengthChecks.length) * 100;
        strengthBar.style.width = strengthPercentage + '%';

        if (strengthPercentage <= 40) {
            strengthBar.className = 'password-strength-weak';
        } else if (strengthPercentage <= 80) {
            strengthBar.className = 'password-strength-medium';
        } else {
            strengthBar.className = 'password-strength-strong';
        }

        // Update validation state
        validationState.password1 = passedChecks === strengthChecks.length;
        if (validationState.password1) {
            formGroup.classList.add('is-valid');
        } else {
            formGroup.classList.add('is-invalid');
        }

        // Trigger confirm password validation if it has a value
        if (password2Input.value) {
            validatePassword2();
        }

        updateSubmitButton();
    }

    // Confirm password validation
    function validatePassword2() {
        const password1 = password1Input.value;
        const password2 = password2Input.value;
        const formGroup = password2Input.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById('password2-feedback');

        formGroup.classList.remove('is-valid', 'is-invalid');
        validationIcon.classList.remove('hidden');

        if (!password2) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Please confirm your password';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.password2 = false;
        } else if (password1 !== password2) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Passwords do not match';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.password2 = false;
        } else {
            formGroup.classList.add('is-valid');
            feedback.textContent = 'Passwords match';
            feedback.className = 'mt-1 text-sm text-green-600';
            validationState.password2 = true;
        }

        updateSubmitButton();
    }

    // Name validation
    function validateName(input, fieldName) {
        const formGroup = input.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById(fieldName + '-feedback');
        const value = input.value.trim();

        formGroup.classList.remove('is-valid', 'is-invalid');
        validationIcon.classList.remove('hidden');

        if (!value) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = fieldName === 'first_name' ? 'First name is required' : 'Last name is required';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState[fieldName] = false;
        } else if (value.length < 2) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Must be at least 2 characters';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState[fieldName] = false;
        } else if (!/^[a-zA-Z\s-']+$/.test(value)) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Only letters, spaces, hyphens and apostrophes allowed';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState[fieldName] = false;
        } else {
            formGroup.classList.add('is-valid');
            feedback.textContent = 'Looks good!';
            feedback.className = 'mt-1 text-sm text-green-600';
            validationState[fieldName] = true;
        }

        updateSubmitButton();
    }

    // Update submit button state
    function updateSubmitButton() {
        // Always enable the submit button to allow form submission
        if (signupButton) {
            signupButton.disabled = false;
            signupButton.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-500');
            signupButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
        }
    }

    // Add event listeners
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }

    if (password1Input) {
        password1Input.addEventListener('input', validatePassword1);
        password1Input.addEventListener('blur', validatePassword1);
    }

    if (password2Input) {
        password2Input.addEventListener('input', validatePassword2);
        password2Input.addEventListener('blur', validatePassword2);
    }

    if (firstNameInput) {
        firstNameInput.addEventListener('input', () => validateName(firstNameInput, 'first_name'));
        firstNameInput.addEventListener('blur', () => validateName(firstNameInput, 'first_name'));
    }

    if (lastNameInput) {
        lastNameInput.addEventListener('input', () => validateName(lastNameInput, 'last_name'));
        lastNameInput.addEventListener('blur', () => validateName(lastNameInput, 'last_name'));
    }

    // Toggle password visibility
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('input');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);

            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    });

    // Initial validation if fields have values
    if (emailInput.value) validateEmail();
    if (password1Input.value) validatePassword1();
    if (password2Input.value) validatePassword2();
    if (firstNameInput.value) validateName(firstNameInput, 'first_name');
    if (lastNameInput.value) validateName(lastNameInput, 'last_name');

    // Initial button state - always enabled
    if (signupButton) {
        signupButton.disabled = false;
        signupButton.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-500');
        signupButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }

    // Form submission
    signupForm.addEventListener('submit', function(e) {
        // Allow form submission regardless of validation state
        // Server-side validation will handle the final check
    });
});
