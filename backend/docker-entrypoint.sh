#!/bin/bash
set -e

if [ "$DEBUG" = "1" ]; then
	shift
	echo "Starting development reloading server"
	exec /usr/bin/python -u /app/whoisapi.py $*
fi

case "$1" in 
	server)
		shift
		echo "Starting gunicorn server"
		exec /usr/bin/gunicorn --timeout $TIMEOUT -w $WORKER_COUNT -b 0.0.0.0:5000 whoisapi:app
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
