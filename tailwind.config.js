module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a56db',
          dark: '#0c4fc7',
          light: '#3b82f6',
        },
        secondary: {
          DEFAULT: '#2d3748',
          dark: '#1a365d',
        },
        accent: {
          DEFAULT: '#f59e0b',
          dark: '#d97706',
        },
      },
      boxShadow: {
        'nav': '0 2px 10px rgba(0, 0, 0, 0.05)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'slide-up': 'slideUp 0.8s ease-out forwards',
        'pulse-slow': 'pulse 3s infinite',
        'float': 'float 3s ease-in-out infinite',
        'bounce-slow': 'bounce 3s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      minHeight: {
        'screen-without-footer': 'calc(100vh - 400px)',
      },
      lineClamp: {
        2: '2',
        3: '3',
        4: '4',
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/forms'),
  ],
}
