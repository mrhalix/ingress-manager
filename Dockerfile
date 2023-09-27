# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables for non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for your application
WORKDIR /app

# Copy the requirements file into the container
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your application will run on (if applicable)
EXPOSE 8080

# Define the command to run your application
CMD ["python", "kuber-operator.py"]
