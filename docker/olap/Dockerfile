FROM docker.io/library/postgres:17-alpine

COPY ["data/olap/01_olap_ddl.sql", "/docker-entrypoint-initdb.d/01_schema.sql"]
COPY ["data/olap/02_olap_views.sql", "/docker-entrypoint-initdb.d/02_views.sql"]
