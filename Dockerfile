# 1) Official Python image
FROM python:3.10-slim

# 2) Working directory inside container
WORKDIR /app

# 3) Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4) Copy only requirements and install first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy project files
COPY . .

# 6) Expose FastAPI default port
EXPOSE 8000

# 7) Run FastAPI app in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
