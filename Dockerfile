# Stage 1: Build the application
FROM python:3.8-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Create the final image
FROM python:3.8-slim

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local

# Set PATH environment variable
ENV PATH=/root/.local/bin:$PATH

# Copy the rest of the application code
COPY src/main.py /app/

# Run the application
CMD ["python", "main.py"]
