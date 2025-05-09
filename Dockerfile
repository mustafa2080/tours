FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    git \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make build.sh executable
RUN chmod +x ./build.sh

# Collect static files
RUN python manage.py collectstatic --no-input --clear

# Skip migrations during build - will be run at container startup
# RUN python manage.py migrate

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Start Gunicorn
CMD ["gunicorn", "tourism_project.wsgi:application", "--bind", "0.0.0.0:8000"]
