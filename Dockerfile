# ─── Stage 1: Build React frontend ───
FROM node:20-alpine AS frontend-build

WORKDIR /app/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --production=false
COPY web/ ./
RUN npm run build

# ─── Stage 2: Python backend ───
FROM python:3.13-slim

# Install git (needed for cloning repos)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py main.py ./
COPY agents/ agents/
COPY services/ services/
COPY orchestration/ orchestration/
COPY schemas/ schemas/
COPY tools/ tools/

# Copy built frontend from stage 1
COPY --from=frontend-build /app/web/dist web/dist/

# Create directory for generated tests
RUN mkdir -p generated_tests

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost/api/health')"

# Run with gunicorn + eventlet for production
CMD ["gunicorn", "--worker-class", "eventlet", "--workers", "1", "--bind", "0.0.0.0:80", "--timeout", "300", "app:app"]
