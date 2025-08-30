# Use an official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system packages for Google Chrome and its repository
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg

# Add Google's official GPG key
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google.gpg
RUN chmod a+r /etc/apt/keyrings/google.gpg

# Add the Chrome repository to Apt sources
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
  | tee /etc/apt/sources.list.d/google-chrome.list

# Update package list and install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Command to run the application when the container starts
# Gunicorn is a production-ready web server with an increased timeout
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]

