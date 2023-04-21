SERVICE ?= fastapi_eth_erc20_txns

.PHONY: ps logs up recreate stop down shell runshell ishell pull test

all: ps

check-service:
ifeq ($(SERVICE),)
	$(error SERVICE is not set)
endif

ps:
	docker-compose ps

logs:
	docker-compose logs -f --tail 100

up:
	docker-compose up -d
	sleep 2
	docker-compose ps

recreate:
	docker-compose up -d --build --force-recreate
	sleep 2
	docker-compose ps

stop:
	docker-compose stop
	docker-compose ps

down:
	docker-compose down
	docker-compose ps

shell: check-service
	docker-compose exec ${SERVICE} bash

runshell: check-service
	docker-compose run ${SERVICE} bash

ishell: check-service
	docker-compose exec ${SERVICE} pip install ipython
	docker-compose exec ${SERVICE} python fastapi_shell.py

pull:
	git pull

# TODO - add tests
test: check-service
	docker-compose exec ${SERVICE} pytest -v
