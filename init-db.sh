#!/bin/bash
set -e

# This runs as the Superuser defined in POSTGRES_USER
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 1. Create Databases using variables from .env
    CREATE DATABASE ${AP_POSTGRES_DATABASE};
    CREATE DATABASE ${API_DB_NAME};

    -- 2. Create Users using variables from .env
    CREATE USER ${AP_POSTGRES_USERNAME} WITH PASSWORD '${AP_POSTGRES_PASSWORD}';
    CREATE USER ${API_DB_USER} WITH PASSWORD '${API_DB_PASSWORD}';

    -- 3. Setup Activepieces Database Permissions
    \c ${AP_POSTGRES_DATABASE};
    GRANT ALL PRIVILEGES ON DATABASE ${AP_POSTGRES_DATABASE} TO ${AP_POSTGRES_USERNAME};
    GRANT ALL ON SCHEMA public TO ${AP_POSTGRES_USERNAME};

    -- 4. Setup FastAPI Database Permissions & Logic
    \c ${API_DB_NAME};
    GRANT ALL PRIVILEGES ON DATABASE ${API_DB_NAME} TO ${API_DB_USER};
    GRANT ALL ON SCHEMA public TO ${API_DB_USER};
    GRANT ALL ON SCHEMA public TO ${API_DB_USER};

    -- 5. Create table logic

    CREATE TYPE grade_label AS ENUM ('APROBADO', 'NOTABLE', 'SOBRESALIENTE', 'MATRICULA');
    ALTER TYPE grade_label OWNER TO ${API_DB_USER};

    CREATE TABLE academic_scales (
        id SERIAL PRIMARY KEY,
        country_name VARCHAR(100) NOT NULL,
        scale_description VARCHAR(255) NOT NULL,
        total_grades INTEGER /*,
        CONSTRAINT unique_country_scale UNIQUE (country_name, scale_description)*/ -- If uncommented, keep , at prev line
    );
    ALTER TABLE academic_scales OWNER TO ${API_DB_USER};

    CREATE TABLE grade_equivalences (
      id SERIAL PRIMARY KEY,
      scale_id INTEGER REFERENCES academic_scales(id) ON DELETE CASCADE,
      origin_grade VARCHAR(50) NOT NULL,
      spanish_5_10 DECIMAL(4, 2) NOT NULL,
      spanish_1_4 INTEGER, -- Optional
      spanish_literal grade_label NOT NULL
    );
    ALTER TABLE grade_equivalences OWNER TO ${API_DB_USER};

    CREATE TABLE api_users (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      active BOOLEAN NOT NULL DEFAULT TRUE,
      api_key VARCHAR(255) NOT NULL UNIQUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      is_internal BOOLEAN NOT NULL DEFAULT TRUE
    );
    ALTER TABLE api_users OWNER TO ${API_DB_USER};

    -- Populate initial data (Scales)
    INSERT INTO academic_scales (id, country_name, scale_description, total_grades) VALUES
    (1, 'AFGANISTAN', '50(1ª)-100(51ª)', 51),
    (2, 'ALBANIA', '5(1ª)-10(6ª)', 6),
    (3, 'ALEMANIA', 'D(1,0)(1ª)-A(4,0)(10ª)', 10),
    (4, 'ALEMANIA', 'D(1,0)(1ª)-A(4,0)(6ª)', 6),
    (5, 'ALEMANIA', 'GE/A(4)(1ª)-SG(1)(4ª)', 5);

    INSERT INTO grade_equivalences (scale_id, origin_grade, spanish_5_10, spanish_1_4, spanish_literal) VALUES
    (1, '50,00', 5.00, 1, 'APROBADO'),
    (1, '65,00', 7.00, 2, 'NOTABLE'),
    (1, '80,00', 9.00, 3, 'SOBRESALIENTE'),
    (1, '100,00', 10.00, 4, 'MATRICULA'),
    (2, '5,00', 5.00, 1, 'APROBADO'),
    (2, '9,00', 7.00, 2, 'NOTABLE'),
    (2, '10,00', 9.00, 3, 'SOBRESALIENTE'),
    (3, 'D', 5.00, 1, 'APROBADO'),
    (3, 'B-', 7.00, 2, 'NOTABLE'),
    (3, 'A', 10.00, 4, 'MATRICULA'),
    (5, 'GE', 5.00, 1, 'APROBADO'),
    (5, 'SG', 9.00, 3, 'SOBRESALIENTE');

    INSERT INTO api_users (name, active, api_key, is_internal)
    VALUES ('activepieces', TRUE, '${FASTAPI_ACTIVEPIECES_API_KEY}', TRUE)
    ON CONFLICT (api_key) DO UPDATE
    SET
      name = EXCLUDED.name,
      active = EXCLUDED.active,
      is_internal = EXCLUDED.is_internal;
    
EOSQL
