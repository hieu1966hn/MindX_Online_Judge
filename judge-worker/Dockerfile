FROM python:3.12-slim

WORKDIR /app

# Copy and install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# CMD placeholder — judge worker entrypoint will be implemented in Phase 5
CMD ["python", "-m", "worker.main"]
