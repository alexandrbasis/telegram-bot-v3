# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# No additional OS packages required; keep image slim

# Copy requirements first (for better caching)
COPY requirements/ ./requirements/

# Install Python dependencies (base set for production image)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/base.txt

# Copy the application source code
COPY src/ ./src/
COPY start_bot.sh ./
COPY .env.example ./

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port (Railway will set PORT env var)
EXPOSE 8080

# Command to run the bot
CMD ["python", "-m", "src.main"]
