# Dockerfile
FROM python:3.9-slim

# Install FFmpeg and dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose port for Flask
EXPOSE 5000

# Start the application with gunicorn
CMD ["gunicorn", "-w", "1", "--timeout", "120", "main:app"]