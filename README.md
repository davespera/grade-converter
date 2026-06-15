# Grade Converter

Grade Converter is a web application for managing academic grading scales and converting grades between systems. It lets you define a scale for a country or institution, store grade equivalences, and convert a batch of grades into consistent output formats.

## What it does

- Manage academic scales and their grade equivalences.
- Convert grades against a selected scale.
- Return conversion results as JSON, CSV, XLSX, or ODS.
- Search scales by country name or description.
- Match a set of grades against a scale to find equivalences.
- Seed the database from the official Spanish grade equivalences dataset.
- Provide a SvelteKit frontend for browsing, searching, and editing scales.
- Support automation workflows through Activepieces, including AI-powered flows.

## Project Layout

- `backend/` FastAPI API and PostgreSQL models.
- `backend/seed.py` Seeds the database from the official Spanish grade equivalences dataset.
- `backend/tests/` Regression tests for scales, search, matching, seeding, auth, and transfer.
- `frontend/` SvelteKit app that interacts to the API.
- `activepieces/` Example Activepieces workflow definitions, including AI-powered flows.
- `proxy/` Traefik configuration for routing the deployed services.
- `docker-compose.yml` Full application stack.
- `justfile` Convenience commands for common Docker workflows.

## Deploy With Docker

### 1. Install prerequisites

You need Docker and Docker Compose.

### 2. Configure environment files

Create your runtime environment files from the examples and fill in the secrets and hostnames:

- `.env` for backend, database, and Activepieces secrets. See `env.example` for the necessary values
- `.env.shared` for shared runtime values such as public URLs.

### 3. Deploy project

Run `just build` to deploy the project. If you don't have `just` installed, you can check the contents of `justfile` to see commands to deploy it.
The flow is as follows

#### 1. Start Traefik

The app stack expects the external `traefik_public` network to exist. Start Traefik first:

```sh
docker compose -f proxy/traefik-docker-compose.yml up -d
```

If the external network is missing, create it once:

```sh
docker network create traefik_public
```

#### 2. Start the application stack

Build and run the app services with the shared environment files:

```sh
docker compose --env-file .env.shared --env-file .env up -d --build
```

## Useful Commands

- `just` lists available recipes.
- `just up` starts the app stack.
- `just down` stops the app stack and removes volumes.
- `just build` rebuilds the full stack.
- `just dev-up` starts the stack in dev mode (foreground output, hot reload).
- `just dev-build` rebuilds and starts in dev mode.
- `just down-proxy` stops the Traefik proxy.
- `just seed` seeds the database from the bundled Spanish equivalences dataset. Accepts `--force` to wipe and re-seed.
- `just gen-api` updates the OpenAPI schema in the frontend (requires backend venv).
- `just gen-api-local` same as `gen-api` but uses the local `node_modules` binary directly.

## Notes

- The backend runs on FastAPI and uses PostgreSQL.
- The frontend is built with SvelteKit and served with the Node adapter.
- The database can be seeded automatically at startup by setting `SEED_ON_STARTUP=true` in `.env`. The seed is idempotent unless `--force` is passed.
- Activepieces workflow definitions live in `activepieces/`. Both standard proxy flows and AI-powered flows (JavaScript and native Pieces variants) are included.
- Some parameters of the Activepieces workflows need to be configured manually (e.g., secrets, Microsoft connections, AI API keys).
