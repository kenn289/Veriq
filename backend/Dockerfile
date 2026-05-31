FROM python:3.12-slim

WORKDIR /app

# Install system deps (if any needed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

# Use pip for simplicity; keep containers small by installing only prod deps
RUN python -m pip install --upgrade pip
RUN pip install .

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "veriq.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
