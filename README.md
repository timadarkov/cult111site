## Запуск через Docker Compose

Все команды ниже выполняются из папки `deploy/`.

### Подготовка

Нужны Docker и Docker Compose.

В корне проекта должны находиться:

- `.env` — настройки приложения;
- `certs/` — ключи для подписи и проверки JWT.

Пример настроек локальной базы в `.env`:

```dotenv
DB_USER=local_user
DB_PASSWORD=replace_with_your_password
DB_NAME=cult111
DB_HOST=localhost
DB_PORT=5432
```

Также заполните остальные настройки, необходимые приложению.

При запуске через Compose адрес базы для бэкенда переопределяется на
`postgres:5432`: `postgres` — имя сервиса базы в общей сети контейнеров.

### Ключи RS256

Если ключей ещё нет, выполните из корня проекта:

```bash
mkdir -p certs
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out certs/private.pem
openssl pkey -in certs/private.pem -pubout -out certs/public.pem
```

Пути в настройках `auth_jwt` должны соответствовать файлам внутри контейнера:

- `/app/certs/private.pem`;
- `/app/certs/public.pem`.

Существующие ключи без необходимости не заменяйте: смена пары ключей
сделает ранее выпущенные токены недействительными.

Не добавляйте `.env` и приватный ключ в Git или Docker-образ.
Они подключаются при запуске контейнера.

### Запуск локально

Из корня проекта перейдите в папку конфигурации:

```bash
cd deploy
```

Соберите и запустите приложение:

```bash
docker compose --env-file ../.env up --build
```

Compose использует базовый файл и `docker-compose.override.yml`.
Запускаются бэкенд и Postgres 17.

После готовности базы скрипт запуска выполняет `alembic upgrade head`,
затем запускает приложение.

Swagger: http://localhost:8000/docs

Для запуска в фоне:

```bash
docker compose --env-file ../.env up --build -d
```

Изменения в подключённых `app/`, `main.py` и `database.py` вызывают
перезагрузку приложения. При изменении зависимостей или Dockerfile
повторите запуск с `--build`.

### Остановка и данные базы

```bash
docker compose --env-file ../.env down
```

Именованный том базы сохраняется. При следующем запуске с тем же
именем Compose-проекта используются прежние данные.

Команда `down -v` удаляет том проекта вместе с данными базы.

### Запуск на продакшене

На сервере подготовьте:

- Docker и Docker Compose;
- файлы проекта;
- серверный `.env` в корне проекта;
- ключи в `certs/`;
- доступную внешнюю базу PostgreSQL.

В серверном `.env` укажите реальные `DB_HOST`, `DB_PORT`, `DB_USER`,
`DB_PASSWORD` и `DB_NAME` внешней базы. Если провайдер требует SSL,
настройте его в подключении приложения.

Из папки `deploy/` выполните:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Dev-файл `docker-compose.override.yml` при этой команде не применяется.

В prod-режиме:

- контейнер Postgres не запускается;
- используется код из образа, без монтирования исходников;
- горячая перезагрузка отключена;
- порт бэкенда на сервере не публикуется;
- миграции выполняются перед запуском приложения.

Доступ через nginx настраивается отдельным этапом.

Проверка состава prod-конфигурации:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --services
```

Ожидаемый результат — только `backend`.

### Логи и диагностика

Логи локального бэкенда:

```bash
docker compose --env-file ../.env logs -f backend
```

Логи локальной базы:

```bash
docker compose --env-file ../.env logs -f postgres
```

Состояние контейнеров:

```bash
docker compose --env-file ../.env ps
```

Логи на продакшене:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
```

Если миграции завершились с ошибкой, приложение не запускается.
Проверьте ошибку в логах, доступность базы и настройки подключения.
После исправления повторите команду запуска.

Если миграционные файлы изменились, пересоберите образ с `--build`:
папка `alembic/` в текущей конфигурации не монтируется с компьютера.

Ошибка `Could not import module` означает, что нужно проверить путь
к модулю приложения. В этом проекте используется `main:app`.

Периодические запросы `GET /docs` — это проверка здоровья контейнера.
Ответ `200 OK` означает, что страница документации доступна.
