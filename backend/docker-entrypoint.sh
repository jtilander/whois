#!/bin/bash
set -e


case "$1" in 
	server)
		shift
		if [ "$DEBUG" = "1" ]; then
			echo "Starting development reloading server"
			exec /usr/bin/python -u /app/whoisapi.py $*
		else
			echo "Starting gunicorn server"
			exec /usr/bin/gunicorn --timeout $TIMEOUT -w $WORKER_COUNT -b 0.0.0.0:5000 whoisapi:app
		fi
		;;
	worker)
		shift

		HUEY_OPTIONS="--worker-type process --workers ${WORKER_COUNT} --localtime ops.huey" 

		if [ "$DEBUG" = "1" ]; then
			HUEY_OPTIONS="--verbose ${HUEY_OPTIONS}"
		fi

		echo "Starting huey worker"
		exec /usr/bin/python -u /usr/bin/huey_consumer.py ${HUEY_OPTIONS} $*
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
