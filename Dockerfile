# One image for the gateway and every agent; docker-compose picks the module to run.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/libs/common:/app

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY libs ./libs
COPY agents ./agents
COPY services ./services

RUN useradd --create-home --uid 1000 portiq && mkdir -p /app/data && chown portiq /app/data
USER portiq

EXPOSE 8000
CMD ["python", "-m", "services.gateway.main"]
