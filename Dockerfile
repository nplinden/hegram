FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app

COPY . /app

EXPOSE 7777

RUN uv sync

RUN uv run python -m hegram.build_dataframes

CMD ["uv", "run", "main.py"]
