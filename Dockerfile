FROM ghcr.io/astral-sh/uv:bookworm-slim

WORKDIR /app

COPY . /app

EXPOSE 7777

CMD ["uv", "run", "main.py"]
