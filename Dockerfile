# Universal reproducible environment for ATRS Requirements Engineering Pipeline
# Team On Top: Yashika Mehra & Shaina Mehra
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install minimal OS dependencies for network & build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all project code, data, prompts, and documentation
COPY . /app/

# Environment configurations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default execution: Run diagnostic check then demo pipeline
CMD ["python", "run_pipeline.py", "--demo"]
