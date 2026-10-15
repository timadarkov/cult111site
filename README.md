# CULT111 — Catalog API

CULT111 is a product catalog with a public storefront and a separate administration panel. The backend provides product, brand, category and information-page APIs, user authentication, administrative access checks, and image storage integration.

Live storefront: [store.cult111.com](https://store.cult111.com/)
Main site: [cult111.com](https://cult111.com/)

Both pages returned HTTP 200 on 15 October 2026. This check confirms availability, not a full end-to-end audit.

## Stack

- Python 3.14 (Docker image), FastAPI, Pydantic / pydantic-settings, Uvicorn.
- PostgreSQL, synchronous SQLAlchemy / psycopg2, Alembic migrations.
- JWT access and refresh tokens signed with RS256; bcrypt password hashing.
- Cloudflare R2 through the S3-compatible boto3 API, presigned image uploads.
- Docker Compose; Nginx reverse proxy and TLS configuration.
- Separate storefront and admin repositories use HTML, CSS, JavaScript and Node.js local servers.

## Related repositories

- Backend: `timadarkov/cult111site` (this repository).
- Storefront: `timadarkov/store111front`.
- Admin panel: `timadarkov/admin111front`.

Repository access depends on visibility settings. Do not advertise these as public source links until the security release checks are complete.

## Features and scope

The public API serves visible products, brands, categories and information pages. Products support brand/category filters. Administrative routes manage catalog content, users and product images. The image code supports uploads, visibility, ordering, main-image selection and copying.

This is a catalog storefront: its order action opens contact information. The inspected code does not implement a public checkout, payment processing or stock by size. The database layer is synchronous.

## Local setup

Prerequisites: Docker with Docker Compose, OpenSSL, and Node.js 20+ for the two frontends. Use development credentials and a separate development database/bucket.

From the backend repository root, create a local settings file only if one does not already exist:

```sh
cp -n .env.example .env
```

Edit `.env` locally. Set `DB_USER`, `DB_NAME`, a new unique `DB_PASSWORD`, `DB_HOST=postgres`, `DB_DIRECT_HOST=postgres`, `DB_PORT=5432`, `DB_SSLMODE=disable` and `ENVIRONMENT=local`. The database host is overridden to `postgres` by the development Compose file. `HOST_URL` and `CORS_ORIGINS` are JSON lists; local frontend origins are `http://localhost:5000` and `http://localhost:5001`.

For working image uploads, configure `R2_ENDPOINT`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET` and `R2_PUBLIC_URL` for a development bucket. The example uses a valid dummy HTTPS endpoint so imports can initialize without real credentials; storage operations require real development settings.

Create a local JWT signing key pair only if these files do not already exist:

```sh
mkdir -p certs
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out certs/private.pem
openssl pkey -in certs/private.pem -pubout -out certs/public.pem
chmod 600 certs/private.pem
```

Replacing an existing signing key invalidates tokens. Do not overwrite production keys for local testing.

Start the development database, then run the backend with an explicit localhost port:

```sh
cd deploy
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml build backend
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml up -d postgres
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml run --rm --no-deps -p 127.0.0.1:8000:8000 backend
```

The final command stays attached. The entrypoint runs `alembic upgrade head` before Uvicorn starts. These commands do not start Nginx, whose current template requires production TLS certificates and server-specific paths. After changing dependencies, rebuild the backend image before running it:

```sh
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml build backend
```

- API base: `http://127.0.0.1:8000/api/v1`
- Development Swagger UI: `http://127.0.0.1:8000/api/docs`
- Development OpenAPI: `http://127.0.0.1:8000/api/openapi.json`
- Health: `http://127.0.0.1:8000/health` (process liveness, not a database/storage probe).

In another terminal, from `deploy/`, create the first administrator interactively if none exists:

```sh
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml run --rm --no-deps backend python -m scripts.create_first_admin
```

The script prompts for credentials and refuses to bootstrap another account if an administrator already exists. Do not put passwords in shell commands.

Stop the attached backend with Ctrl+C. To stop development services while preserving the database volume:

```sh
docker compose --env-file ../.env -f docker-compose.yml -f docker-compose.override.yml down
```

Do not add `-v` unless you intend to delete the local database volume. Changing `DB_PASSWORD` in `.env` alone does not change the password of an existing PostgreSQL role.

## Storefront and admin

Start the backend first, then run each frontend from its own repository:

```sh
# storefront repository
API_ORIGIN=http://127.0.0.1:8000 npm run start:front
# admin repository, in a separate terminal
API_ORIGIN=http://127.0.0.1:8000 npm start
```

Open `http://localhost:5000` and `http://localhost:5001`. The Node servers proxy requests to the backend. The admin panel requires an account with `is_admin=true`.

## Deployment

The production Compose overlay reads `.env.prod`. Pass that file explicitly for Compose interpolation as well:

```sh
cd deploy
docker compose --env-file ../.env.prod -f docker-compose.yml -f docker-compose.prod.yml config --services
```

The base file includes `backend`, `nginx` and an optional `certbot` tools profile. Production uses an external PostgreSQL database. Before starting production, configure the deployment paths, `SERVER_NAME`, database SSL settings and TLS certificates required by the Nginx template. The template also references other hosted sites; review it for your deployment rather than assuming it is portable.

## Verification

The backend includes focused unittest tests in `tests/test_image_settings.py`. They use in-memory SQLite and mocked storage, not the production database. Running them requires the application dependencies and HTTPX, which is not currently listed in `requirements.txt`:

```sh
python -m pip install httpx
python tests/test_image_settings.py
```

Both frontend repositories provide `npm run check` and `npm test`. Test availability does not imply full coverage or continuous integration.

## Security before publication

The exposed local database password has been rotated and a sanitized history has been prepared in an isolated copy. Publication remains blocked until that history is applied, old GitHub references are addressed, and potential exposure from previously shared Docker images is resolved. A clean default secret-scanner result alone is insufficient for short/default database passwords.

Environment files and private signing keys must stay out of Git and Docker build contexts. Existing images built before `.env.prod` was excluded need review; if an image containing secrets was shared, rotate those credentials and replace the image. Repository visibility changes and history rewrites require the owner's explicit approval after remediation.
