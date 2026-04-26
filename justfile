up:
    docker compose --env-file .env.shared --env-file .env up

down:
    docker compose --env-file .env.shared --env-file .env down -v
