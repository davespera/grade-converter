build:
    docker compose --env-file .env.shared --env-file .env up --build
up:
    docker compose --env-file .env.shared --env-file .env up 
down:
    docker compose --env-file .env.shared --env-file .env down -v
