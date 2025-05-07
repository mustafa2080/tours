# Tourism Project

A comprehensive tourism website with multi-language support, booking system, and payment integration.

## Setup Instructions

### Local Development

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tourism_project
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   npm install
   ```

4. Create a `.env` file:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file and add your configuration values.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Build static assets:
   ```
   npm run build
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

### Environment Variables

The project uses environment variables for configuration. These are loaded from a `.env` file in development. In production (e.g., on Render), these are set as environment variables.

#### Critical Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `True` in development, `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string

#### Payment Integration

- `PAYPAL_MODE`: Either `sandbox` or `live`
- `PAYPAL_CLIENT_ID`: Your PayPal client ID
- `PAYPAL_SECRET`: Your PayPal secret key

#### Social Authentication

- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

## Deployment to Render

This project is configured for deployment on Render.com.

1. Push your code to GitHub (make sure `.env` is in `.gitignore`).

2. Create a new Web Service on Render:
   - Connect your GitHub repository
   - Select "Python" as the environment
   - Set the build command to `./build.sh`
   - Set the start command to `gunicorn tourism_project.wsgi:application`

3. Add environment variables in the Render dashboard:
   - All the variables from your `.env` file (except development-specific ones)
   - Set `RENDER=true` to enable Render-specific settings

4. Deploy the service.

## Security Notes

- Never commit `.env` files or any files containing secrets to version control.
- Use environment variables for all sensitive information.
- In production, always use HTTPS and set appropriate security headers.
