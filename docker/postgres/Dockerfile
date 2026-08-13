FROM docker.io/library/postgres:17-alpine

COPY ["Fontes de dados - Pet Shop Nosso Aumigo/03_Itabuna_ddl.sql", "/docker-entrypoint-initdb.d/01_schema.sql"]
COPY ["Fontes de dados - Pet Shop Nosso Aumigo/04_itabuna_dml.sql", "/docker-entrypoint-initdb.d/02_data.sql"]
