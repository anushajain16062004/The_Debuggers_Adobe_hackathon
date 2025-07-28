FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including required libraries for PyMuPDF (fitz)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libcrypt-dev \
    libssl3 \
    # Additional dependencies for PyMuPDF
    libjpeg-dev \
    zlib1g-dev \
    # Create symlink for libcrypt if needed
    && ln -s /usr/lib/x86_64-linux-gnu/libcrypt.so.1 /usr/lib/x86_64-linux-gnu/libcrypt.so.2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/collections

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "analyze:application"]