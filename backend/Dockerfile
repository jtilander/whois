FROM alpine:3.5

RUN apk add --no-cache \
		py-pip \
		py-raven \
		py-requests \
		python \
		curl \
		bash \
		py-gunicorn

ENV VISUAL=vi WORKER_COUNT=8 TIMEOUT=300

RUN pip --disable-pip-version-check --no-cache-dir install flask flask_restful flask-cors elasticsearch

RUN mkdir /data && mkdir /input && mkdir /app
VOLUME ["/data", "/input"]

COPY whoisapi.py config.py /app/

WORKDIR /app

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["server"]
