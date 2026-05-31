# Grade Converter

Grade Converter is a web application for managing academic grading scales and converting grades between systems. It lets you define a scale for a country or institution, store grade equivalences, and convert a batch of grades into consistent output formats.

## What it does

- Manage academic scales and their grade equivalences.
- Convert grades against a selected scale.
- Return conversion results as JSON, CSV, XLSX, or ODS.
- Provide a SvelteKit frontend for browsing and editing scales.
- Support automation workflows through Activepieces.

## Project Layout

- `backend/` FastAPI API and PostgreSQL models.
- `frontend/` SvelteKit app that interacts to the API.
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

- `just up` starts the app stack.
- `just down` stops the app stack and removes volumes.
- `just build` rebuilds the full stack.

## Notes

- The backend runs on FastAPI and uses PostgreSQL.
- The frontend is built with SvelteKit and served with the Node adapter.