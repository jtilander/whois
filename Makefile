.PHONY: iterate up down kill build clean

export DEBUG?=0
export DATADIR?=./tmp/data

DC=docker-compose
DC_FLAGS="-p whois"

iterate: kill build up

up:
	@$(DC) $(DC_FLAGS) up -d && $(DC) $(DC_FLAGS) logs -f

down:
	@$(DC) $(DC_FLAGS) down

kill:
	@$(DC) $(DC_FLAGS) down -v

build:
	@$(DC) $(DC_FLAGS) build

# Clean through a docker container
clean:
	docker run --rm -v "`pwd`/tmp:/mnt" alpine:3.5 /bin/sh -c 'rm -f /mnt/data/photos/*'
	docker run --rm -v "`pwd`/tmp:/mnt" alpine:3.5 /bin/sh -c 'rm -f /mnt/data/users.json'
	docker run --rm -v "`pwd`/tmp:/mnt" alpine:3.5 /bin/sh -c 'rm -rf /mnt/esdata'
