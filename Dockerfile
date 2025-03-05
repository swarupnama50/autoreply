# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install necessary system dependencies
RUN apt-get update \
    && apt-get install -y \
    wget \
    ca-certificates \
    curl \
    libx11-xcb1 \
    libx11-6 \
    libxcomposite1 \
    libxrandr2 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libgdk-pixbuf2.0-0 \
    libx11-dev \
    libnss3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables
ENV MESSENGER_EMAIL=your-email@example.com
ENV MESSENGER_PASSWORD=your-password

# Run the script
CMD ["python", "main.py"]
