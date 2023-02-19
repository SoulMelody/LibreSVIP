FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUTF8=1
COPY ./ /app

RUN pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple/ --global && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without=dev,ffmpeg,desktop && \
    rm -rf /root/.cache/pip && \
    rm -rf /root/.cache/pypoetry

EXPOSE 8080
CMD ["/usr/bin/python", "-m", "libresvip.web", "--exec_mode=main", "--server", "--port=8080"]