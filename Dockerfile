# syntax = docker/dockerfile:1.5

FROM python:3.11-slim as base
WORKDIR /app
COPY ./ /app

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/ --global && \
    pip install pdm && \
    pdm config python.use_venv false && \
    pdm sync --prod -G webui -G ujson

EXPOSE 8080
CMD ["pdm", "run", "libresvip-web", "--port=8080", "--host=0.0.0.0", "--server", "--daemon"]