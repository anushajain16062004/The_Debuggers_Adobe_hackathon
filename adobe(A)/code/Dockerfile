# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy everything into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your script
CMD ["python", "round1a.py"]
