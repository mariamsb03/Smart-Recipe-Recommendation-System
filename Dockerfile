# ============ Stage 1: Build Frontend ============
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy ALL configuration files first
COPY frontend/ ./

# Install dependencies
RUN npm ci

# Copy the rest of the source code
COPY frontend/src ./src
COPY frontend/public ./public

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

COPY backend/ ./backend/

# Copy the Flask app file as app.py to root
COPY backend/app.py ./app.py  

# Frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Use JSON array format
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:\"${PORT}\" --workers 2 --threads 2 --timeout 120 app:app"]
