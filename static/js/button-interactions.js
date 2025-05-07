/**
 * Button Interactions - Enhances button states and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all buttons in the document
    const buttons = document.querySelectorAll('button, .btn, [type="submit"]');
    
    // Add interaction effects to each button
    buttons.forEach(button => {
        // Skip buttons that already have event listeners
        if (button.dataset.interactionInitialized) return;
        
        // Mark as initialized
        button.dataset.interactionInitialized = 'true';
        
        // Add ripple effect on click
        button.addEventListener('click', function(e) {
            // Only add ripple if button doesn't have .no-ripple class
            if (!this.classList.contains('no-ripple')) {
                const rect = this.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const ripple = document.createElement('span');
                ripple.classList.add('ripple-effect');
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;
                
                this.appendChild(ripple);
                
                // Remove ripple after animation completes
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            }
            
            // Add active state
            this.classList.add('active');
            
            // Remove active state after a delay
            setTimeout(() => {
                this.classList.remove('active');
            }, 300);
        });
        
        // Add hover state
        button.addEventListener('mouseenter', function() {
            this.classList.add('hover');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
        
        // Add focus state
        button.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        button.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });
    
    // Special handling for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Skip forms that already have event listeners
        if (form.dataset.interactionInitialized) return;
        
        // Mark as initialized
        form.dataset.interactionInitialized = 'true';
        
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('[type="submit"]');
            if (submitButton) {
                // Add loading state
                submitButton.classList.add('loading');
                
                // Store original text
                if (!submitButton.dataset.originalText) {
                    submitButton.dataset.originalText = submitButton.innerHTML;
                }
                
                // Replace with loading indicator if not already done
                if (!submitButton.querySelector('.fa-spinner')) {
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>' + 
                                           (submitButton.textContent || 'Loading...');
                }
                
                // Disable to prevent double submission
                submitButton.disabled = true;
            }
        });
    });
});

// Add CSS for ripple effect
document.addEventListener('DOMContentLoaded', function() {
    // Create style element if it doesn't exist
    if (!document.getElementById('button-interaction-styles')) {
        const style = document.createElement('style');
        style.id = 'button-interaction-styles';
        style.textContent = `
            .ripple-effect {
                position: absolute;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.4);
                width: 100px;
                height: 100px;
                margin-top: -50px;
                margin-left: -50px;
                animation: ripple 0.6s linear;
                transform: scale(0);
                pointer-events: none;
            }
            
            @keyframes ripple {
                to {
                    transform: scale(2.5);
                    opacity: 0;
                }
            }
            
            button, .btn, [type="submit"] {
                position: relative;
                overflow: hidden;
            }
            
            button.loading, .btn.loading, [type="submit"].loading {
                opacity: 0.8;
                cursor: wait;
            }
        `;
        document.head.appendChild(style);
    }
});
