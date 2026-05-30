FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/pyproject.toml backend/README.md /app/
COPY backend/veriq /app/veriq
COPY backend/alembic /app/alembic
COPY backend/alembic.ini /app/alembic.ini

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "veriq.main:app", "--host", "0.0.0.0", "--port", "8000"]
