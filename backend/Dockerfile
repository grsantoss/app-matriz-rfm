FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy config directory
COPY ../config /app/config

# Add config to PYTHONPATH
ENV PYTHONPATH=/app

# Create required directories
RUN mkdir -p /app/storage/analysis_history

# Expose port
EXPOSE 5173

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5173", "--reload"]