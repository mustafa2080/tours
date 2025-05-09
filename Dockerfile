FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    gcc \
    git \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Copy requirements and build script first
COPY requirements.txt build.sh ./

# Make build.sh executable
RUN chmod +x ./build.sh

# Copy package.json for npm dependencies
COPY package*.json ./

# Copy the rest of the application
COPY . .

# Run the build script
RUN ./build.sh

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "tourism_project.wsgi:application", "--bind", "0.0.0.0:8000"]
