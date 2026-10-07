FROM ghcr.io/astral-sh/uv:bookworm-slim

# Liberation Sans, which stands in for Arial in the PDF worksheets (Typst reads system fonts; Ezra SIL ships
# with the app), and curl for health checks.
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-liberation2 curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

EXPOSE 5844

# Install the exact versions pinned in uv.lock; fails if the lock is out of date with pyproject.toml.
RUN uv sync --locked --no-dev --group build

RUN uv run --no-sync python -m hegram.build_dataframes

# 2 worker processes (~250 MB each, mostly the in-memory corpus) with 4 threads each.
CMD ["uv", "run", "--no-sync", "gunicorn", "--bind", "0.0.0.0:5844", "--workers", "2", "--threads", "4", "--timeout", "60", "wsgi:server"]
