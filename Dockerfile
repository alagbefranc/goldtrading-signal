FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Environment variables should be set at runtime
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "forex_bot.py"]
