# Multi-stage Dockerfile for testing jetq across different Python versions
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dev.txt .
COPY pyproject.toml .
COPY setup.py .
COPY README.md .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY jetq/ ./jetq/
COPY tests/ ./tests/
COPY examples/ ./examples/

# Install the package in development mode
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command runs all tests
CMD ["pytest", "-v", "--tb=short"]
