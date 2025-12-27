# Use official Python slim image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install the dependencies
RUN uv sync --no-dev

# Expose the port Uvicorn will run on
EXPOSE 8080

# Run the FastAPI app with Uvicorn
CMD ["uv", "run", "python", "main.py"]
