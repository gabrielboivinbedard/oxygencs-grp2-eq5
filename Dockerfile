# Stage 1: Build the application
FROM python:3.8-alpine AS builder

EXPOSE 8000

WORKDIR /app

# Install build dependencies
RUN apk update \
 && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file and install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.8-alpine
WORKDIR /app
COPY --from=builder /root/.local /root/.local
# Set PATH environment variable
ENV PATH=/root/.local/bin:$PATH

# Copy the rest of the application code
COPY src/ /app/src/

RUN rm -rf /tmp
RUN rm -rf /var/cache
# Run the application
CMD ["python", "src/main.py"]
