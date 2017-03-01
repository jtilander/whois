DOCKER_REPO?=jtilander
DOCKER_NAME?=whois_frontend
TAG?=test
PORTS=-p 9000:80
VOLUMES=-v `pwd`/app:/app

.PHONY: image push run debug clean nuke

image:
	@docker build -t $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) .
	@docker images $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

push:
	@docker push $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

run:
	@docker run --rm $(PORTS) $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)

debug:
	@docker run --rm -it $(PORTS) $(VOLUMES) $(ENVIRONMENT) $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG) /bin/sh

clean:
	@echo "Clean"

nuke: clean
	@-docker rm -f `docker ps -q -a -f ancestor=$(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`
	@-docker rmi -f `docker images -q -a $(DOCKER_REPO)/$(DOCKER_NAME):$(TAG)`
