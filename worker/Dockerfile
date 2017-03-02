FROM alpine:3.5

RUN apk add --no-cache \
		py-pip \
		py-gevent \
		py-redis \
		python \
		bash \
		git

ENV VISUAL=vi WORKER_COUNT=8 TIMEOUT=300

ENV HUEY_VERSION=1fbffc7d8ea099bb195d8cb0b4c8841e9fb13ce6
#RUN pip --disable-pip-version-check --no-cache-dir install huey
RUN git clone https://github.com/coleifer/huey.git /tmp/huey && cd /tmp/huey && git checkout $HUEY_VERSION && python setup.py install && rm -rf /tmp/huey


RUN mkdir /data && mkdir /app
VOLUME ["/data", "/app"]

WORKDIR /app

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["worker"]
