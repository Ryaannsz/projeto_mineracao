FROM docker.io/library/postgres:17-alpine

COPY ["data/postgres/03_itabuna_ddl.sql", "/docker-entrypoint-initdb.d/01_schema.sql"]
COPY ["data/postgres/04_itabuna_dml.sql", "/docker-entrypoint-initdb.d/02_data.sql"]
