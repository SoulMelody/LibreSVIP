# syntax = docker/dockerfile:1.5
FROM python:3.11 as builder
WORKDIR /app
COPY ./ /app

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i "s|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g" /etc/apt/sources.list.d/debian.sources

RUN apt-get update -y && apt-get install -y --no-install-recommends libmediainfo-dev

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/ --global && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without=desktop,dev,test,code_gen,packaging --with=webui,ujson

FROM python:3.11-slim as base
WORKDIR /app
COPY ./ /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

EXPOSE 8080
CMD ["python", "-m", "libresvip.web", "--port=8080", "--host=0.0.0.0"]