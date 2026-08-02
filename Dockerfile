FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# 1. Set environment variables early
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 2. Setup persistent directory first
RUN mkdir -p /app/data && chown -R nobody:nogroup /app/data

# 3. Install dependencies using uv cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --python 3.10

# 4. Copy project source code
COPY . /app
RUN chown -R nobody:nogroup /app

# 5. Drop root privileges for safety
USER nobody

CMD ["python", "main.py"]
