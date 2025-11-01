# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for layer caching)
COPY requirements.txt .

# Install dependencies (no cache to keep image small)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

# Run your worker
CMD ["python", "app/scripts/worker.py"]
