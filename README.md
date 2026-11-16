
## Running with Docker Compose

Unless stated otherwise, run the commands below from the `deploy/` directory.

### Prerequisites

Docker and Docker Compose must be installed.

The project root must contain:

- `.env` — application settings;
- `certs/` — keys for signing and verifying JWTs.

Also configure any other settings required by the application.

When running through Compose, the backend’s database address is overridden to `postgres:5432`. Here, `postgres` is the database service name on the shared container network.

### RS256 Keys

If you do not have keys yet, run the following from the project root:

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

The final command stays attached. The entrypoint runs `alembic upgrade head` before Uvicorn starts. These commands start the backend without Nginx. For local development, Nginx can be started separately using the HTTP-only configuration in deploy/nginx/local.conf. Production Nginx uses HTTPS with TLS certificates. After changing dependencies, rebuild the backend image before running it:

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

Production runs as Compose project `deploy` in
`/home/deploy/cult111site`.

Run production commands from the repository root. Production requires
`.env.prod`, JWT keys in `certs/`, TLS certificates in `certbot/`,
and the frontend directories referenced by Compose.

These files and credentials must be provisioned on the server separately.
Do not commit secrets or edit tracked files directly on the server.

### GitHub Actions deployment

The CD workflow currently supports manual deployment:

1. Merge the reviewed PR into `main` after CI passes.
2. Open GitHub Actions → CD → Run workflow.
3. Select `main` and start the workflow.
4. Check that deployment and the public health check both pass.

Required repository secrets:

- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_KNOWN_HOSTS`

The workflow checks the server repository, updates it to the triggering
commit, builds the backend image, validates Nginx configuration, and
recreates the backend and Nginx containers.

Database migrations run automatically through `deploy/entrypoint.sh`
before the backend starts. A migration failure prevents application startup.

Deployment briefly interrupts the production service. A failed workflow
does not automatically restore the previous version.

The public health check requests `https://cult111.com/health` and verifies
the JSON response. This checks API availability through HTTPS and Nginx;
it does not verify database or object storage availability.

### Production diagnostics

Run from `/home/deploy/cult111site` on the server:

```bash
docker compose \
  --project-name deploy \
  --env-file .env.prod \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  ps
```

View recent backend and Nginx logs:

```bash
docker compose \
  --project-name deploy \
  --env-file .env.prod \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  logs --tail 100 backend nginx
```

Check the public endpoint:

```bash
curl --fail --show-error https://cult111.com/health
```

### Rollback

A rollback must restore application code compatible with the current
database schema. Reverting Git commits does not undo database migrations.

Before rolling back, inspect the deployment logs and identify the faulty
change. The deployment log includes `Previous commit`, which identifies
the server repository revision before that deployment.

For a code rollback:

1. Create a rollback branch from a freshly updated `main`.
2. Revert the faulty commit or commits using `git revert`.
3. Open a PR, run CI, and obtain review.
4. Merge the rollback PR into `main`.
5. Run the CD workflow manually on `main`.
6. Verify the public health endpoint and the affected application behavior.

Example for one ordinary, non-merge commit, run locally:

```bash
git switch main
git pull --ff-only origin main
git switch -c fix/rollback-production
git revert <FAULTY_COMMIT_SHA>
git push -u origin fix/rollback-production
```

Replace `<FAULTY_COMMIT_SHA>` with the actual faulty commit.
For a merge commit, inspect its parents and select the correct mainline
before using `git revert -m`; do not apply the example blindly.

Revert preserves shared Git history and creates a new commit containing
the undo operation. Do not force-push or reset production `main` backward.

If a migration removed or changed data required by the previous code,
prepare a compatible corrective migration or use a verified database
recovery procedure before redeploying. Do not blindly run
`alembic downgrade` on production.


## Dependency Management

Python dependencies are managed with **Poetry 2.x**.

- `pyproject.toml` — declares direct dependencies and version constraints.
- `poetry.lock` — locks exact versions of all dependencies.
- `requirements.txt` — generated from `poetry.lock` for Docker builds.

### Dependency Groups

- `main` — production dependencies required by the application.
- `dev` — development and testing tools (`pytest`, `pytest-asyncio`, `httpx`).

### Setup

Install Poetry separately from the project environment.

Configure Poetry to create `.venv` inside the project:

```bash
poetry config virtualenvs.in-project true --local
```

Install production and development dependencies:

```bash
poetry install
```

Install only production dependencies:

```bash
poetry install --only main
```

Run commands inside the Poetry environment:

```bash
poetry run python --version
poetry run pytest
```

### Managing Dependencies

Add a production dependency:

```bash
poetry add <package>
```

Add a development dependency:

```bash
poetry add --group dev <package>
```

Remove a production dependency:

```bash
poetry remove <package>
```

Update dependencies:

```bash
poetry update
```

### Exporting requirements.txt

The Dockerfile installs Python packages from `requirements.txt`.

**This file is generated from `poetry.lock` and must not be edited manually.**

Install the Poetry export plugin:

```bash
poetry self add poetry-plugin-export
```

After changing dependencies, regenerate `requirements.txt`:

```bash
poetry export --only main --without-hashes -o requirements.txt
```

Only production dependencies are exported. Development dependencies are excluded.

Rebuild the Docker image after updating `requirements.txt`.

Always commit `pyproject.toml`, `poetry.lock`, and `requirements.txt` together.

## Testing

The project uses pytest for automated testing.

### Requirements

- Python 3.14
- Poetry
- Docker and Docker Compose
- PostgreSQL 17

### Test database

Tests use a separate PostgreSQL database named `cult111_test`.

The database runs inside the existing development PostgreSQL container.

Start PostgreSQL:

```bash
docker compose \
  --env-file .env \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.override.yml \
  up -d postgres
```

Create the test database if it does not exist:

```bash
docker compose \
  --env-file .env \
  -f deploy/docker-compose.yml \
  -f deploy/docker-compose.override.yml \
  exec postgres sh -c \
  'createdb -U "$POSTGRES_USER" cult111_test'
```

Add the following variables to `.env`:

```dotenv
TEST_DB_HOST=127.0.0.1
TEST_DB_PORT=5433
TEST_DB_NAME=cult111_test
```

The PostgreSQL container must expose port `5433` on localhost.

### Running tests

Install dependencies:

```bash
poetry install
```

Run all tests:

```bash
poetry run pytest
```

Run the product integration test:

```bash
poetry run pytest tests/test_products.py -v
```

### Database isolation

- Tests never intentionally use the application's production database.
- The database name must be `cult111_test`.
- Each test receives its own SQLAlchemy session.
- Database changes are rolled back after each test.
- Test tables are created before testing and removed afterward.
- The test runner refuses to use a database containing existing tables.

Do not use production database credentials or production PostgreSQL servers for tests.

## Tests and coverage

Run tests with coverage:

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Run the linter:

```bash
poetry run ruff check .
```
