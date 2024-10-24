FROM python:3.13-slim as base
WORKDIR /app
COPY ./ /app

RUN pip install pdm && \
    pdm config python.use_venv false && \
    pdm sync --prod -G webui -G ujson -G ruamel_yaml -G lxml && \
    rm -rf ~/.cache/pip && \
    rm -rf ~/.cache/pdm

EXPOSE 8080
CMD ["pdm", "run", "libresvip-web", "--port=8080", "--host=0.0.0.0", "--server", "--daemon"]