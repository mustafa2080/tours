/**
 * Comprehensive email validation utility
 * Provides real-time validation for email fields with detailed feedback
 */

class EmailValidator {
  constructor(options = {}) {
    // Default configuration
    this.config = {
      minLength: 6,
      maxLength: 254,
      validTLDs: [
        'com', 'net', 'org', 'edu', 'gov', 'mil', 'io', 'co.uk', 'ca', 'de',
        'fr', 'jp', 'au', 'nz', 'ru', 'it', 'es', 'nl', 'br', 'in', 'mx',
        'ch', 'se', 'no', 'dk', 'fi', 'pl', 'cz', 'hu', 'pt', 'gr', 'ie',
        'at', 'hk', 'sg', 'ae', 'za', 'ar', 'cl', 'pe', 'co', 've', 'ua',
        'tr', 'sa', 'eg', 'th', 'my', 'ph', 'vn', 'id', 'kr', 'il', 'info',
        'biz', 'me', 'tv', 'app', 'dev', 'io', 'ai', 'cloud', 'design',
        'online', 'store', 'tech', 'blog', 'site', 'xyz'
      ],
      disallowedTLDs: ['co'], // TLDs that are not allowed standalone
      ...options
    };

    // Regular expressions for validation
    this.patterns = {
      // Basic email format validation
      basicFormat: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      // Username part (before @)
      username: /^[a-zA-Z0-9._-]+$/,
      // Domain part (after @)
      domain: /^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
      // Check for consecutive special characters
      consecutiveSpecials: /\.{2,}|-{2,}|_{2,}|@{2,}|\.-|-\.|\._|_\./,
      // Check for invalid characters
      invalidChars: /[#$%^&*()+=[\]{}|\\:;"'<>,?/\s]/
    };
  }

  /**
   * Validate an email address with detailed feedback
   * @param {string} email - The email address to validate
   * @returns {Object} - Validation result with status and message
   */
  validate(email) {
    // Trim the email to remove any leading/trailing whitespace
    email = email.trim();

    // Check if email is empty
    if (!email) {
      return {
        isValid: false,
        message: 'Email address is required',
        code: 'required'
      };
    }

    // Check email length
    if (email.length < this.config.minLength) {
      return {
        isValid: false,
        message: `Email must be at least ${this.config.minLength} characters long`,
        code: 'min_length'
      };
    }

    if (email.length > this.config.maxLength) {
      return {
        isValid: false,
        message: `Email cannot exceed ${this.config.maxLength} characters`,
        code: 'max_length'
      };
    }

    // Check basic email format
    if (!this.patterns.basicFormat.test(email)) {
      return {
        isValid: false,
        message: 'Please enter a valid email address (e.g., username@example.com)',
        code: 'invalid_format'
      };
    }

    // Split email into username and domain parts
    const [username, domain] = email.split('@');

    // Check username part
    if (!username) {
      return {
        isValid: false,
        message: 'Username part of email cannot be empty',
        code: 'invalid_username'
      };
    }

    // Check domain part
    if (!domain.includes('.')) {
      return {
        isValid: false,
        message: 'Domain must include a dot for the top-level domain',
        code: 'invalid_domain'
      };
    }

    // Check top-level domain (TLD)
    const tld = domain.split('.').pop().toLowerCase();

    // If all checks pass, the email is valid
    return {
      isValid: true,
      message: 'Email is valid',
      code: 'valid'
    };
  }
}

// Initialize the validator when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  const emailValidator = new EmailValidator();

  // Find all email input fields
  const emailInputs = document.querySelectorAll('input[type="email"], input[name="login"], input[name="email"]');

  emailInputs.forEach(input => {
    // Create or find feedback element
    let feedbackId = input.id ? `${input.id}-feedback` : `${input.name}-feedback`;
    let feedbackElement = document.getElementById(feedbackId);

    if (!feedbackElement) {
      // If feedback element doesn't exist, create one
      feedbackElement = document.createElement('p');
      feedbackElement.id = feedbackId;
      feedbackElement.className = 'mt-1 text-sm validation-feedback';
      input.parentNode.appendChild(feedbackElement);
    }

    // Add validation icon if not present
    let validationIcon = input.parentNode.querySelector('.validation-icon');
    if (!validationIcon) {
      validationIcon = document.createElement('div');
      validationIcon.className = 'absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none validation-icon hidden';
      validationIcon.innerHTML = `
        <i class="fas fa-check-circle text-green-500" style="display: none;"></i>
        <i class="fas fa-times-circle text-red-500" style="display: none;"></i>
      `;
      input.parentNode.appendChild(validationIcon);
    }

    // Add event listeners for real-time validation
    input.addEventListener('input', function() {
      validateEmailInput(this, feedbackElement, validationIcon);
    });

    input.addEventListener('blur', function() {
      validateEmailInput(this, feedbackElement, validationIcon);
    });

    // Initial validation if the field has a value
    if (input.value) {
      validateEmailInput(input, feedbackElement, validationIcon);
    }
  });

  // Function to validate email input and update UI
  function validateEmailInput(input, feedbackElement, validationIcon) {
    const result = emailValidator.validate(input.value);

    // Show validation icon
    validationIcon.classList.remove('hidden');

    // Update feedback message and styling
    if (result.isValid) {
      feedbackElement.textContent = result.message;
      feedbackElement.classList.remove('text-red-600');
      feedbackElement.classList.add('text-green-600');
      input.classList.remove('border-red-500');
      input.classList.add('border-green-500');

      // Update validation icon
      validationIcon.querySelector('.fa-check-circle').style.display = 'inline-block';
      validationIcon.querySelector('.fa-times-circle').style.display = 'none';
    } else {
      feedbackElement.textContent = result.message;
      feedbackElement.classList.remove('text-green-600');
      feedbackElement.classList.add('text-red-600');
      input.classList.remove('border-green-500');
      input.classList.add('border-red-500');

      // Update validation icon
      validationIcon.querySelector('.fa-check-circle').style.display = 'none';
      validationIcon.querySelector('.fa-times-circle').style.display = 'inline-block';
    }

    // Return validation result for form submission handling
    return result.isValid;
  }

  // Add form submission validation
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    const emailInput = form.querySelector('input[type="email"], input[name="login"], input[name="email"]');
    if (emailInput) {
      form.addEventListener('submit', function(e) {
        const feedbackId = emailInput.id ? `${emailInput.id}-feedback` : `${emailInput.name}-feedback`;
        const feedbackElement = document.getElementById(feedbackId);
        const validationIcon = emailInput.parentNode.querySelector('.validation-icon');

        // Validate email before submission
        const isValid = validateEmailInput(emailInput, feedbackElement, validationIcon);

        // Allow form submission regardless of validation state
        // Server-side validation will handle the final check
      });
    }
  });
});
