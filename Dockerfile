# Dockerfile for RAG Knowledge Base Assistant (Hugging Face API)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Install CPU-only PyTorch first to avoid huge CUDA downloads (saves ~2GB)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch>=2.0.0,<3.0.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p chroma_db docs config

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Start the application
CMD ["python", "main.py"]

