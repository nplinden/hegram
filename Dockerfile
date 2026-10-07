FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app

COPY . /app

EXPOSE 7777

RUN uv sync --no-dev --group build

RUN uv run --no-sync python -m hegram.build_dataframes

CMD ["uv", "run", "--no-sync", "main.py"]
