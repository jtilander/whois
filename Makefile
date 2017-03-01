.PHONY: iterate up down kill build clean

export DEBUG?=0
export DATADIR?=../ldapmunge/tmp

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

clean:
	rm -rf ./tmp && mkdir -p ./tmp
