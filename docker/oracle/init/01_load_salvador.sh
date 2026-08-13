#!/usr/bin/env bash
set -euo pipefail

readonly DATA_DIR=/dados

# O DML fornecido esta em ISO-8859-1; informe a codificacao ao cliente SQL*Plus.
export NLS_LANG=AMERICAN_AMERICA.WE8ISO8859P1

sqlplus -s "${APP_USER}/${APP_USER_PASSWORD}@//localhost:1521/FREEPDB1" <<SQL
WHENEVER OSERROR EXIT FAILURE
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET SQLBLANKLINES ON
@${DATA_DIR}/01_salvador_ddl.sql
@${DATA_DIR}/02_salvador_dml.sql
COMMIT;
EXIT SUCCESS
SQL
