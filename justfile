default:
    just --list
build:
    docker compose -f proxy/traefik-docker-compose.yml up -d --build && docker compose --env-file .env.shared --env-file .env up -d --build
up:
    docker compose -f proxy/traefik-docker-compose.yml up -d && docker compose --env-file .env.shared --env-file .env up -d
down:
    docker compose --env-file .env.shared --env-file .env down -v
dev-build:
    docker compose -f proxy/traefik-docker-compose.yml up -d --build && docker compose --env-file .env.shared --env-file .env up --build
dev-up:
    docker compose -f proxy/traefik-docker-compose.yml up -d && docker compose --env-file .env.shared --env-file .env up 
down-proxy:
    docker compose -f proxy/traefik-docker-compose.yml down
seed *ARGS:
    docker compose --env-file .env.shared --env-file .env exec backend python -m backend.seed {{ARGS}}
gen-api:
    backend/venv/bin/python -m backend.export_openapi frontend/.openapi.json
    cd frontend && npm run gen-api
gen-api-local:
    backend/venv/bin/python -m backend.export_openapi frontend/.openapi.json
    cd frontend && ./node_modules/.bin/openapi-typescript .openapi.json -o ./src/lib/api/schema.d.ts
