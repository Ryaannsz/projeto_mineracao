FROM docker.io/gvenzl/oracle-free:23-slim

COPY ["Fontes de dados - Pet Shop Nosso Aumigo/01_salvador_ddl.sql", "/dados/01_salvador_ddl.sql"]
COPY ["Fontes de dados - Pet Shop Nosso Aumigo/02_salvador_dml.sql", "/dados/02_salvador_dml.sql"]
COPY --chmod=755 docker/oracle/init/01_load_salvador.sh /container-entrypoint-initdb.d/01_load_salvador.sh
