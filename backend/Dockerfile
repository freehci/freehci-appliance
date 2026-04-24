FROM python:3.12-slim

# Subnett-skann (ICMP) og MAC via `ip neigh` — slim-imaget har ikke disse som standard.
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping iproute2 git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/alembic.ini .
COPY backend/alembic ./alembic
COPY backend/app ./app
COPY backend/docker-entrypoint.sh /docker-entrypoint.sh
COPY .ver /app/.ver

RUN chmod +x /docker-entrypoint.sh \
    && mkdir -p /app/data/uploads /app/data/mibs \
    && groupadd --gid 10001 freehci \
    && useradd --uid 10001 --gid freehci --system --no-create-home freehci \
    && chown -R freehci:freehci /app

ENV PYTHONPATH=/app

USER root

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
