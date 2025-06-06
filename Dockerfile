#  Stage 1: Base build stage
FROM python:3.8-slim AS builder

# Create the app directory
RUN mkdir /usr/src/app

#  Set the working directory
WORKDIR /usr/src/app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy the requirements file first (better caching)
COPY ./requirements.txt .

#  Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#  copy project
COPY . .

#  RUN python manage.py migrate