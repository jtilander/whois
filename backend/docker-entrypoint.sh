#!/bin/bash
set -e

case "$1" in 
	server)
		shift
		echo "Starting gunicorn server"
		exec /usr/bin/gunicorn -w $WORKER_COUNT -b 0.0.0.0:5000 whoisapi:app
		;;
	debug)
		shift
		echo "Starting development reloading server"
		exec /usr/bin/python -u /app/whoisapi.py $*
		;;
	bash)
		shift
		exec /bin/bash $*
		;;
	pingtest)
		exec /bin/ping -c 10 8.8.8.8
		;;
esac

exec "$@"
