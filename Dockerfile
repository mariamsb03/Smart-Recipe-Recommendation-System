# ==================================
# Multi-Stage Dockerfile
# Frontend (React/Vite) + Backend (Flask + ML)
# ==================================

# ============ Stage 1: Build Frontend ============
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend dependency files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production
RUN npm run build


# ============ Stage 2: Backend + Serve Frontend ============
FROM python:3.10-slim

WORKDIR /app

# ---------- System dependencies ----------
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Backend source ----------
COPY backend/ .

# ---------- Frontend build ----------
# Flask will serve this directory
COPY --from=frontend-builder /frontend/dist ./static

# ---------- Runtime directories ----------
RUN mkdir -p /app/uploads

# ---------- Environment ----------
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
# Railway sets $PORT dynamically - default to 8080 for local
ENV PORT=8080

# ---------- Expose port ----------
EXPOSE 8080

# ---------- Health check ----------
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# ---------- Start app ----------
# Use sh -c to evaluate $PORT at runtime
CMD sh -c "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 2 --timeout 120 app:app"
