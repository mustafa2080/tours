# Comprehensive Email Validation

This document outlines the comprehensive email validation implementation for both login and signup forms in the Tourism Project.

## Features

The email validation system includes the following features:

### 1. Required Field Validation
- Ensures the email field is not empty
- Provides clear error messages for empty fields

### 2. Format Validation
- Verifies the email follows a valid format (username@domain.com)
- Ensures exactly one "@" symbol
- Requires at least one "." after the "@" for the domain
- Username validation:
  - Can include letters (a-z, A-Z), numbers (0-9), dots (.), hyphens (-), or underscores (_)
  - No consecutive special characters (e.g., .., --, or @-)
- Domain validation:
  - Must include letters, numbers, hyphens, and at least one dot for the top-level domain
  - The top-level domain must be fully specified and valid (e.g., ".com", ".org", ".net")
  - Specifically, ".co" is not allowed as a standalone TLD; it must be ".com" for domains like example.com
  - No consecutive dots or special characters

### 3. Length Validation
- Minimum length of 6 characters
- Maximum length of 254 characters (per email standards)

### 4. Account Creation Specific
- Checks if the email is already registered in the database (must be unique)
- Provides clear error messages for duplicate emails

### 5. Login Specific
- Verifies the email exists in the database for login attempts
- Uses a generic error message for security (prevents user enumeration)

### 6. Security Considerations
- Prevents SQL injection by sanitizing input
- Prevents XSS attacks by escaping special characters
- Case-insensitive matching for email (e.g., User@example.com = user@example.com)

### 7. User Feedback
- Provides clear, localized error messages for each validation failure
- Real-time validation feedback as the user types (client-side)
- Server-side validation to ensure consistency

## Implementation

The validation is implemented at both client-side and server-side levels:

### Client-Side Validation

1. **JavaScript Validation Class (`email-validation.js`)**
   - Provides real-time validation as the user types
   - Shows visual feedback with icons and messages
   - Validates against all the rules mentioned above

2. **Integration with Forms**
   - Works with both login and signup forms
   - Provides immediate feedback to users

### Server-Side Validation

1. **Django Forms**
   - `CustomSignupForm` - Validates emails for new account creation
   - `CustomLoginForm` - Validates emails for login attempts

2. **Django Adapters**
   - `CustomAccountAdapter` - Provides comprehensive email validation for signup
   - Ensures all validation rules are enforced before account creation

## Valid Top-Level Domains (TLDs)

The system recognizes the following TLDs as valid:

```
'com', 'net', 'org', 'edu', 'gov', 'mil', 'io', 'co.uk', 'ca', 'de', 
'fr', 'jp', 'au', 'nz', 'ru', 'it', 'es', 'nl', 'br', 'in', 'mx', 
'ch', 'se', 'no', 'dk', 'fi', 'pl', 'cz', 'hu', 'pt', 'gr', 'ie', 
'at', 'hk', 'sg', 'ae', 'za', 'ar', 'cl', 'pe', 'co', 've', 'ua', 
'tr', 'sa', 'eg', 'th', 'my', 'ph', 'vn', 'id', 'kr', 'il', 'info', 
'biz', 'me', 'tv', 'app', 'dev', 'io', 'ai', 'cloud', 'design', 
'online', 'store', 'tech', 'blog', 'site', 'xyz'
```

## Disallowed Standalone TLDs

The following TLDs are not allowed as standalone domains:

```
'co'
```

## Error Messages

The system provides specific error messages for different validation failures:

- "Email address is required."
- "Email must be at least 6 characters long."
- "Email cannot exceed 254 characters."
- "Email must contain an '@' symbol."
- "Email must contain exactly one '@' symbol."
- "Username part of email cannot be empty."
- "Username can only contain letters, numbers, dots, hyphens, or underscores."
- "Username cannot contain consecutive special characters."
- "Domain part of email cannot be empty."
- "Domain must include a dot for the top-level domain."
- "Domain must be valid and include a top-level domain."
- "Domain cannot contain consecutive special characters."
- "Invalid top-level domain: '.co' is not allowed. Use a complete domain like '.com'."
- "Invalid top-level domain: '.xyz' is not recognized."
- "This email address is already registered. Please use a different email or log in."
- "The email or password you entered is incorrect." (for login attempts)

## Files Modified

1. **JavaScript Files**
   - `static/js/email-validation.js` (new file)
   - `static/js/signup-validation.js` (updated)
   - `static/js/login-validation.js` (updated)

2. **Python Files**
   - `users/adapters.py` (updated)
   - `users/forms.py` (updated)

3. **Templates**
   - `templates/account/signup.html` (updated)
   - `templates/account/login.html` (updated)

4. **Settings**
   - `tourism_project/settings.py` (already configured)

## Usage

The validation system works automatically for all email input fields in the login and signup forms. No additional configuration is needed.

## Testing

To test the validation:

1. Try entering invalid emails (missing @, invalid TLDs, etc.)
2. Try entering emails with consecutive special characters
3. Try entering emails that are too short or too long
4. Try signing up with an email that's already registered
5. Try logging in with an email that doesn't exist

The system should provide appropriate feedback for each case.
