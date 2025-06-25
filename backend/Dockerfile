# backend/Dockerfile
FROM python:3.13

WORKDIR /app

# 1. Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy project source
COPY . .

# 3. Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 4. Default command
ENTRYPOINT ["/app/entrypoint.sh"]
