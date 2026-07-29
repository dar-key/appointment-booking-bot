FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Prevent bytecode writing & enable uv caching
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies using uv.lock (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

# Copy project files
COPY . /app

# Create directory for persistent SQLite database
RUN mkdir -p /app/data

# Put virtual environment on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run the bot
CMD ["python", "main.py"]
