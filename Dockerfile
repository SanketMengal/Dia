# Use an official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the whole project
COPY . /app/

# Expose port for Gunicorn
EXPOSE 8000

# Run Gunicorn server (better than Django dev server)
CMD ["gunicorn", "mydiagramstudio.wsgi:application", "--bind", "0.0.0.0:8000"]
