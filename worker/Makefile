DOCKER_REPO?=jtilander
DOCKER_NAME?=whois_worker
TAG?=test
PORTS=
VOLUMES=-v `pwd`/../backend:/app

.PHONY: image push run debug clean nuke

image:
	@docker build -t $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) .
	@docker images $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

push:
	@docker push $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

run:
	@docker run --rm $(PORTS) $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

debug:
	@docker run --rm -it $(PORTS) $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) bash

clean:
	@echo "Clean"

nuke: clean
	@-docker rm -f `docker ps -q -a -f ancestor=$(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`
	@-docker rmi -f `docker images -q -a $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`
