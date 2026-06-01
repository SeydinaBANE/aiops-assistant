FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-group dev --no-editable

FROM python:3.12-slim

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ src/
COPY scripts/ scripts/
COPY data/ data/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import http.client; http.client.HTTPConnection('localhost', ${API_PORT:-8000}).request('GET', '/health'); assert http.client.HTTPConnection('localhost', ${API_PORT:-8000}).getresponse().status == 200"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "src.main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
