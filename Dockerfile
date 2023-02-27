FROM kitware/trame:ubuntu-20.04-py39

COPY --chown=trame-user:trame-user ./deploy /deploy

RUN /opt/trame/setup.sh && /opt/trame/build.sh && rm -rf /home/trame-user/.cache/pip

COPY ./libresvip $TRAME_VENV/lib/python3.9/site-packages

CMD ["/opt/trame/run.sh"]