# --- Stage 1: Build the Next.js Frontend ---
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Build Next.js project static files to /frontend/out/
RUN npm run build

# --- Stage 2: Create the Python Runtime ---
FROM python:3.12-slim
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/app ./app
COPY backend/test_services.py ./

# Copy built frontend static files to /workspace/static
COPY --from=frontend-builder /frontend/out/ ./static

# Expose the default port for Hugging Face Spaces
EXPOSE 7860

# Run uvicorn on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
