FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUTF8=1
COPY ./ /app

RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/web/simple/ --global && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without=desktop,dev,test,code_gen,ffmpeg,packaging --with=webui,ujson,midi,subtitle,protobuf,text,svg,xml,binary && \
    rm -rf /root/.cache/pip && \
    rm -rf /root/.cache/pypoetry

EXPOSE 8080
CMD ["python", "-m", "libresvip.web", "--port=8080", "--host=0.0.0.0"]