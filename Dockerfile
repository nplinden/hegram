FROM ghcr.io/astral-sh/uv:bookworm-slim

# System libraries WeasyPrint needs to render the PDF worksheets, and the Noto fonts the worksheets use.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

EXPOSE 7777

RUN uv sync --no-dev --group build

RUN uv run --no-sync python -m hegram.build_dataframes

# 2 workers so a slow PDF in one doesn't block the other (~330 MB each at peak), 4 threads each for light requests.
CMD ["uv", "run", "--no-sync", "gunicorn", "--bind", "0.0.0.0:7777", "--workers", "2", "--threads", "4", "--timeout", "60", "wsgi:server"]
