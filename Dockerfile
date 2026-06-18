# Use python slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/user \
    USE_TF=0 \
    USE_FLAX=0

# Create a non-root user (UID 1000 is required by Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set up working directory
WORKDIR /app

# Install system dependencies (needed for certain PyTorch/caching operations)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install python packages
COPY --chown=user:user requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY --chown=user:user . /app/

# Switch to home directory for model caching
USER user

# Train intent classifier during build stage
RUN python train_intent_model.py

# Cache Hugging Face models and NLTK data during build stage
RUN python download_models.py

# Expose Hugging Face default port
EXPOSE 7860

# Run FastAPI app with Uvicorn on port 7860
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "7860"]
