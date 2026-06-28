# Use official Debian slim Python runtime
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for GDAL, PostGIS, OpenCV, and spatial computations
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    gdal-bin \
    python3-gdal \
    libgl1 \
    libglib2.0-0 \
    libproj-dev \
    libgeos-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure GDAL environment variables for Rasterio/GDAL compilation
ENV CPL_ZIP_ENCODING=UTF-8
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . /app/

# Expose API port
EXPOSE 8000

# Start command (overridden in docker-compose for worker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
