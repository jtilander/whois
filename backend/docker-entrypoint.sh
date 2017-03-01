#!/bin/bash
set -e

case "$1" in 
	server)
		shift
		exec /usr/bin/python /app/whoisapi.py $*
		;;
	debug)
		shift
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
