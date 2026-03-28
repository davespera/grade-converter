-- Create Table for countries and their scales
CREATE TABLE academic_scales (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    scale_description VARCHAR(255) NOT NULL,
    total_grades INTEGER,
    -- Ensures business-logic uniqueness:
    CONSTRAINT unique_country_scale UNIQUE (country_name, scale_description)
);

-- Create Table for grade mappings
CREATE TABLE grade_equivalences (
  id SERIAL PRIMARY KEY,
  scale_id INTEGER REFERENCES academic_scales(id) ON DELETE CASCADE,
  origin_grade VARCHAR(50) NOT NULL,
  spanish_5_10 DECIMAL(4, 2) NOT NULL,
  spanish_1_4 INTEGER NOT NULL,
  spanish_literal VARCHAR(50) NOT NULL
);

