# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./flask/ .

# Expose port and start the app
ENV FLASK_APP=app.py 
EXPOSE 5000
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000", "--reload"]
