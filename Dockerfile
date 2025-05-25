# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required packages
RUN pip install fastapi uvicorn prometheus-client

# Copy the main application file
COPY main.py .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]