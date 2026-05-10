FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir datasets huggingface_hub tqdm accelerate

# Copy all necessary source code
COPY backend/ ./backend/
COPY ai/ ./ai/
COPY dataset.py .

# Expose port
EXPOSE 8000

# Run FastAPI using uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
