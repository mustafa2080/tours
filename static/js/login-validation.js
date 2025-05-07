document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');
    const loginButton = document.querySelector('button[type="submit"]');

    // Track validation state
    const validationState = {
        email: false,
        password: false
    };

    // Email validation
    function validateEmail() {
        const email = emailInput.value.trim();
        const formGroup = emailInput.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById('login-feedback');
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

    // Password validation
    function validatePassword() {
        const password = passwordInput.value;
        const formGroup = passwordInput.closest('.form-group');
        const validationIcon = formGroup.querySelector('.validation-icon');
        const feedback = document.getElementById('password-feedback');

        formGroup.classList.remove('is-valid', 'is-invalid');
        validationIcon.classList.remove('hidden');

        if (!password) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Password is required';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.password = false;
        } else if (password.length < 8) {
            formGroup.classList.add('is-invalid');
            feedback.textContent = 'Password must be at least 8 characters';
            feedback.className = 'mt-1 text-sm text-red-600';
            validationState.password = false;
        } else {
            formGroup.classList.add('is-valid');
            feedback.textContent = 'Password is valid';
            feedback.className = 'mt-1 text-sm text-green-600';
            validationState.password = true;
        }

        updateSubmitButton();
    }

    // Update submit button state
    function updateSubmitButton() {
        // Always enable the submit button to allow form submission
        if (loginButton) {
            loginButton.disabled = false;
            loginButton.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-500');
            loginButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
        }
    }

    // Add event listeners
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
        passwordInput.addEventListener('blur', validatePassword);
    }

    // Toggle password visibility
    const togglePassword = document.querySelector('.toggle-password');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    }

    // Initial validation if fields have values
    if (emailInput.value) validateEmail();
    if (passwordInput.value) validatePassword();

    // Initial button state - always enabled
    if (loginButton) {
        loginButton.disabled = false;
        loginButton.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-gray-500');
        loginButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }

    // Form submission
    loginForm.addEventListener('submit', function(e) {
        // Allow form submission regardless of validation state
        // Server-side validation will handle the final check

        // Add active class to button to show it's being clicked
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.classList.add('active');

            // Add loading state
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>' + submitButton.innerText;
        }
    });
});
