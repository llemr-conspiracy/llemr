# makefile

start-dev:
	docker-compose up

start-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

stop-compose:
	@eval docker stop $$(docker ps -a -q)
	docker-compose down

ssh-nginx:
	docker exec -it nginx_server bash

ssh-django-web:
	docker exec -it osler_app bash

ssh-db:
	docker exec -it osler_db bash

build:
	docker-compose build

rebuild:
	docker-compose build --no-cache
	docker-compose up

test:
	docker-compose run osler_app python osler/manage.py test

cleanup:
	docker system prune
