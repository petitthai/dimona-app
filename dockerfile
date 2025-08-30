# Use an official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system packages for Google Chrome
RUN apt-get update && apt-get install -y wget gnupg

# Add Google Chrome's official repository and install Chrome
RUN wget -q -O - [https://dl-ssl.google.com/linux/linux_signing_key.pub](https://dl-ssl.google.com/linux/linux_signing_key.pub) | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] [http://dl.google.com/linux/chrome/deb/](http://dl.google.com/linux/chrome/deb/) stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Command to run the application when the container starts
# Gunicorn is a production-ready web server
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
