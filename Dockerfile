# ============ Stage 1: Build Frontend ============
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the source code
COPY frontend/ ./

# Build argument
ARG VITE_API_URL=https://flavorfit-production-83c1.up.railway.app/api

# Build
RUN VITE_API_URL=${VITE_API_URL} npm run build


# ============ Stage 2: Backend + Serve Frontend ============
FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend to current directory (not /app/backend)
COPY backend/ ./

# Now app.py is at /app/app.py directly
# Test that app.py exists
RUN ls -la /app/app.py || echo "app.py not found" && ls -la /app/

# If needed, rename your Flask app variable to 'app'
# (Make sure in your app.py you have: app = Flask(__name__))

# Frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Simple CMD
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
