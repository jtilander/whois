FROM alpine:3.5

RUN apk add --no-cache \
		py-pip \
		py-raven \
		py-requests \
		py-redis \
		py2-pyldap \
		python \
		curl \
		bash \
		py-gunicorn

ENV VISUAL=vi WORKER_COUNT=8 TIMEOUT=300

RUN pip --disable-pip-version-check --no-cache-dir install \
	elasticsearch==6.3.0 \
	filelock==3.0.4 \
	Flask-Cors==3.0.6 \
	Flask-RESTful==0.3.6 \
	Flask==1.0.2 \
	huey==1.10.0 \
	phonenumbers==8.9.9 \
	&&  \
	pip --disable-pip-version-check --no-cache-dir freeze




# ENV HUEY_VERSION=1fbffc7d8ea099bb195d8cb0b4c8841e9fb13ce6
# RUN apk add --no-cache git && git clone https://github.com/coleifer/huey.git /tmp/huey && cd /tmp/huey && git checkout $HUEY_VERSION && python setup.py install && rm -rf /tmp/huey

RUN mkdir /data && mkdir /input && mkdir /app && mkdir /app/tasks && mkdir /app/scripts
VOLUME ["/data", "/input"]

COPY *.py /app/
COPY scripts/* /app/scripts/
COPY tasks/* /app/tasks/

WORKDIR /app

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["server"]
