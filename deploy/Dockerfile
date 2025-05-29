# ----- STAGE 1: builder -----
FROM python:3.12-slim AS builder

# Create app directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_BUILDKIT=1

COPY requirements.txt .

# Configure extra index for PyTorch CPU wheels
RUN pip config set global.extra-index-url https://download.pytorch.org/whl/cpu

# Copy and install Python dependencies
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache \
    pip install --prefix=/install -r requirements.txt

# Copy application code
COPY . .

# ----- STAGE 2: runtime -----
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --from=builder /app /app

# Set unbuffered stdout/stderr
ENV PYTHONUNBUFFERED=1

# Default entrypoint
CMD ["python3", "-u", "src/main.py"]