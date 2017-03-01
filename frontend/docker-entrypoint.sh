#!/bin/sh
set -e

case "$1" in 
	server)
		shift
		exec /usr/sbin/nginx -g 'daemon off;' $*
		;;
esac

exec "$@"
