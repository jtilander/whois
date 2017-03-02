#!/bin/bash
set -e

WORKERS=8
HUEY_OPTIONS="--worker-type process --workers ${WORKERS} ops.huey"

if [ "$DEBUG" = "1" ]; then
	shift
	echo "Starting development server"
	exec /usr/bin/python -u /usr/bin/huey_consumer.py --verbose ${HUEY_OPTIONS} $*
fi

case "$1" in 
	worker)
		shift
		echo "Starting huey worker"
		exec /usr/bin/python -u /usr/bin/huey_consumer.py ${HUEY_OPTIONS} $*
		;;
	bash)
		shift
		exec /bin/bash $*
		;;
esac

exec "$@"
