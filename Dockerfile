FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir "psycopg[binary]" gunicorn

# Copy application files
COPY . .

# Expose port
EXPOSE 8500

# Start server with Gunicorn Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "leadhunter.web.app:app", "--bind", "0.0.0.0:8500"]
