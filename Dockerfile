FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# dnd_api.py requires a .env file to exist; seed it with the default API config.
# Runtime environment variables still take precedence over these defaults.
RUN cp .env.example .env

# Serve the Flet app as a headless web app (not a desktop window)
ENV FLET_WEB=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
