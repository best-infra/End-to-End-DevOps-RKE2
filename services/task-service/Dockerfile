FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install security updates and dependencies in one layer
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc pkg-config && \
    apt-get install -y --no-install-recommends default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# Copy only necessary files
COPY app.py .

EXPOSE 8002

USER nobody

CMD ["python", "app.py"]
