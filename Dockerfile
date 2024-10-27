FROM python:3.13-slim as base
WORKDIR /app
COPY ./ /app

RUN pip install uv && \
    export UV_SYSTEM_PYTHON=true && \
    uv sync --extra webui --extra ujson --extra ruamel_yaml --extra lxml && \
    rm -rf ~/.cache/pip && \
    uv cache clean

EXPOSE 8080
CMD ["uv", "run", "libresvip-web", "--port=8080", "--host=0.0.0.0", "--server", "--daemon"]