#!/bin/sh
set -eu

cd /home/deploy/cult111site

COMPOSE="docker compose --env-file .env.prod -f deploy/docker-compose.yml -f deploy/docker-compose.prod.yml"

# Проверяем сертификаты и продлеваем при необходимости
$COMPOSE run --rm --no-deps certbot renew --quiet

# Nginx перечитывает сертификаты
$COMPOSE exec -T nginx nginx -s reload
