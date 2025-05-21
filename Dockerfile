# Use a Python base image
FROM python:3.11-slim

# Install system dependencies including root SSL certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && update-ca-certificates

# Set working directory inside container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your bot code
COPY . .

# Run your bot
CMD ["python", "main.py"]
