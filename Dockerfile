FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG TORCH_DEVICE=cpu

# Copy requirements first for better caching
COPY requirements.txt .

# Install base Python dependencies (without torch/torchvision)
RUN pip install --no-cache-dir -r requirements.txt

# Conditionally install torch/torchvision for CPU or GPU
RUN if [ "$TORCH_DEVICE" = "gpu" ]; then \
      pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cu121 torch==2.3.1 torchvision==0.18.1; \
    else \
      pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.3.1 torchvision==0.18.1; \
    fi

# Copy application code
COPY App.py ./
COPY src/ ./src/
COPY models/ ./models/


# Create necessary directories
RUN mkdir -p "uploads/UI image"

# Copy uploads (sample images and UI assets)
COPY uploads/ ./uploads/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "App.py", "--server.port=8501", "--server.address=0.0.0.0"]
