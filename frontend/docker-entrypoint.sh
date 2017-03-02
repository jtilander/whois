#!/bin/sh
set -e

case "$1" in 
	server)
		shift
		if [ ! -f /data/photos/404.jpg ];then
			if [ ! -d /data/photos ]; then
				mkdir /data/photos
			fi
			cp /app/404.jpg /data/photos/404.jpg
		fi
		exec /usr/sbin/nginx -g 'daemon off;' $*
		;;
esac

exec "$@"
