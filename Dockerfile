# syntax=docker/dockerfile:1.7
#
# One image holds the whole application: the web UI and the order logic.
#
# Multi-stage build:
#   base     -> shared Python runtime settings
#   builder  -> resolves and installs dependencies into /opt/venv (uv, cached)
#   runtime  -> slim final image: venv + app code + collected static files
#
# Build:  docker build --build-arg APP_VERSION=$(git rev-parse --short HEAD) -t onward-order-app .
# Run:    docker run -p 8000:8000 --read-only --tmpfs /tmp onward-order-app
#
# ECS runs the container with a read-only root filesystem; only /tmp is writable.

ARG PYTHON_VERSION=3.12

# ---------------------------------------------------------------- base
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ---------------------------------------------------------------- builder
FROM base AS builder

# uv installs packages 10-100x faster than pip.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

RUN uv venv /opt/venv

# Only the requirement files are copied here, so this layer is rebuilt
# when dependencies change, not on every code change.
COPY requirements/ requirements/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python /opt/venv/bin/python -r requirements/prod.txt \
    # Translation sources (.po) are not used at runtime; compiled .mo files stay.
    && find /opt/venv -name '*.po' -delete

# ---------------------------------------------------------------- runtime
FROM base AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    PORT=8000

# Fixed numeric UID/GID so ECS can verify the container runs as non-root.
ARG APP_UID=10001
RUN groupadd --system --gid "${APP_UID}" app \
    && useradd --system --uid "${APP_UID}" --gid app --home-dir /app --no-create-home app \
    && install -d -o app -g app /app/staticfiles

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app manage.py ./
COPY --chown=app:app src/ src/

USER ${APP_UID}:${APP_UID}

# Collect static files at build time: the root filesystem is read-only at runtime.
RUN python manage.py collectstatic --noinput --verbosity 0

# Short git SHA shown on the page and in /health. Declared last so a new
# release only rebuilds this layer.
ARG APP_VERSION=local
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

# PORT comes from the ECS task definition; /tmp is the only writable path.
# The gunicorn control socket is off: it would try to write outside /tmp.
# Tune at runtime with GUNICORN_CMD_ARGS, e.g. "--workers 4 --timeout 60".
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --chdir src --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --worker-tmp-dir /tmp --no-control-socket --access-logfile -"]
