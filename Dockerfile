FROM python:3.11-slim

# Install ffmpeg for video merging (needed for YouTube best quality)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create download directory in /tmp for Railway ephemeral storage
RUN mkdir -p /tmp/downloads

# Expose port 8000 for health checks
EXPOSE 8000

CMD ["python", "bot.py"]
