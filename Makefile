.PHONY: image push run debug clean nuke first

export host_data_root?=/mnt/datavolumes/elasticsearch
export cluster_name?=whois_test

export DOCKER_REPO ?= jtilander
DOCKER_NAME=whois
export TAG ?= test

DATAVOLUMES ?= `pwd`/tmp
INPUTVOLUME ?= `pwd`/input

DEBUG?=0

DC=docker-compose
DC_FLAGS="-p whois"

ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

VOLUMES=-v $(INPUTVOLUME):/input -v $(DATAVOLUMES):/data
ENVIRONMENT=-e "DEBUG=$(DEBUG)"

first: run

image:
	@docker build -t $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) .
	@docker images $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

push:
	@docker push $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

run:
	@docker run --rm $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) $(RUN_ARGS)

debug:
	@docker run --rm -it $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) bash

clean:
	@rm -rf `pwd`/tmp
	@mkdir tmp


nuke: clean
	@-docker rm -f `docker ps -q -a -f ancestor=$(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`
	@-docker rmi -f `docker images -q -a $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`

up:
	@$(DC) $(DC_FLAGS) up -d && $(DC) $(DC_FLAGS) logs -f

down:
	@$(DC) $(DC_FLAGS) down

kill:
	@$(DC) $(DC_FLAGS) down -v
