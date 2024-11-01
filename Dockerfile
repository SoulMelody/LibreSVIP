FROM ghcr.io/astral-sh/uv:debian-slim
WORKDIR /app
COPY ./ /app

RUN uv sync --extra webui --extra ujson --extra ruamel_yaml --extra lxml --frozen --no-cache

EXPOSE 8080
CMD ["uv", "run", "libresvip-web", "--port=8080", "--host=0.0.0.0", "--server", "--daemon"]