
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

```bash
mkdir -p certs
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out certs/private.pem
openssl pkey -in certs/private.pem -pubout -out certs/public.pem
```

The paths in the `auth_jwt` settings must match the files inside the container:

- `/app/certs/private.pem`;
- `/app/certs/public.pem`.

Do not replace existing keys unnecessarily: replacing the key pair will invalidate previously issued tokens.

Do not commit `.env` or the private key to Git or include them in the Docker image. They are mounted when the container starts.

### Running Locally

From the project root, navigate to the configuration directory:

```bash
cd deploy
```

Build and start the application:

```bash
docker compose --env-file ../.env up --build
```

Compose uses the base file and `docker-compose.override.yml`. It starts the backend and PostgreSQL 17.

Once the database is ready, the startup script runs `alembic upgrade head`, then starts the application.

Swagger: http://localhost:8000/docs

To run in the background:

```bash
docker compose --env-file ../.env up --build -d
```

Changes to the mounted `app/` directory, `main.py`, and `database.py` trigger an application reload. After changing dependencies or the Dockerfile, run the startup command again with `--build`.

### Stopping Containers and Keeping Database Data

```bash
docker compose --env-file ../.env down
```

The named database volume is preserved. The next startup uses the existing data, provided the Compose project name remains the same.

The `down -v` command deletes the project’s database volume and its data.

### Running in Production

Prepare the following on the server:

- Docker and Docker Compose;
- the project files;
- a server-specific `.env` file in the project root;
- keys in `certs/`;
- an accessible external PostgreSQL database.

In the server’s `.env`, set `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` to the external database’s connection details. If the provider requires SSL, configure it in the application’s database connection.

From the `deploy/` directory, run:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

This command does not apply the development file, `docker-compose.override.yml`.

In production:

- no PostgreSQL container is started;
- the application uses code from the image, without mounting source files;
- automatic code reloading is disabled;
- the backend port is not published on the host;
- migrations run before the application starts.

Access through nginx is configured in a separate step.

To check which services are included in the production configuration:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --services
```

The output should contain only `backend`.

### Logs and Troubleshooting

Local backend logs:

```bash
docker compose --env-file ../.env logs -f backend
```

Local database logs:

```bash
docker compose --env-file ../.env logs -f postgres
```

Container status:

```bash
docker compose --env-file ../.env ps
```

Production logs:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
```

If migrations fail, the application will not start. Check the error in the logs, database availability, and connection settings. After fixing the issue, run the startup command again.

If migration files have changed, rebuild the image with `--build`: the `alembic/` directory is not mounted from the host in the current configuration.

A `Could not import module` error means you should check the application module path. This project uses `main:app`.

Periodic `GET /docs` requests come from the container health check. A `200 OK` response means the documentation page is accessible.
