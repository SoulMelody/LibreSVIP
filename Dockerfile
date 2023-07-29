# syntax = docker/dockerfile:1.5
FROM python:3.11 as builder
WORKDIR /app
COPY ./ /app

RUN sed -i "s/archive.ubuntu.com/mirrors.ustc.edu.cn/g" /etc/apt/sources.list \
    && sed -i "s|security.ubuntu.com|mirrors.ustc.edu.cn|g" /etc/apt/sources.list

RUN apt-get update -y && apt-get install -y --no-install-recommends libmediainfo-dev

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/ --global && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without=desktop,dev,test,code_gen,ffmpeg,packaging --with=webui,ujson,midi,subtitle,protobuf,text,svg,xml,binary

FROM python:3.11-slim as base
WORKDIR /app
COPY ./ /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

EXPOSE 8080
CMD ["python", "-m", "libresvip.web", "--port=8080", "--host=0.0.0.0"]