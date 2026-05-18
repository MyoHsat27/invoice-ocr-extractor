FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV BACKEND_ROOT=/app/backend

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml /app/backend/pyproject.toml
COPY backend/src /app/backend/src
RUN pip install --no-cache-dir /app/backend

COPY backend/tests /app/backend/tests

EXPOSE 8000

CMD ["uvicorn", "invoice_agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
