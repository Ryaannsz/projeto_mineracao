from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote_plus

import oracledb
import psycopg
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database


@dataclass(frozen=True)
class ConfiguracaoBancos:
    oracle_host: str
    oracle_port: int
    oracle_service: str
    oracle_user: str
    oracle_password: str
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str
    mongodb_uri: str
    mongodb_database: str


def carregar_configuracao() -> ConfiguracaoBancos:
    load_dotenv()
    mongo_user = quote_plus(os.getenv("MONGO_ROOT_USER", "root"))
    mongo_password = quote_plus(os.getenv("MONGO_ROOT_PASSWORD", "Mongo123"))
    mongo_host = os.getenv("MONGODB_HOST", "localhost")
    mongo_port = os.getenv("MONGO_PORT", "27017")

    return ConfiguracaoBancos(
        oracle_host=os.getenv("ORACLE_HOST", "localhost"),
        oracle_port=int(os.getenv("ORACLE_PORT", "1521")),
        oracle_service=os.getenv("ORACLE_SERVICE", "FREEPDB1"),
        oracle_user=os.getenv("ORACLE_USER", "petshop"),
        oracle_password=os.getenv("ORACLE_USER_PASSWORD", "Petshop123"),
        postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_database=os.getenv("POSTGRES_DB", "petshop_itabuna"),
        postgres_user=os.getenv("POSTGRES_USER", "petshop"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "Postgres123"),
        mongodb_uri=os.getenv(
            "MONGODB_URI",
            f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/?authSource=admin",
        ),
        mongodb_database=os.getenv("MONGO_DATABASE", "petshop_feira"),
    )


def conectar_oracle(configuracao: ConfiguracaoBancos | None = None):
    configuracao = configuracao or carregar_configuracao()
    dsn = oracledb.makedsn(
        configuracao.oracle_host,
        configuracao.oracle_port,
        service_name=configuracao.oracle_service,
    )
    return oracledb.connect(
        user=configuracao.oracle_user,
        password=configuracao.oracle_password,
        dsn=dsn,
    )


def conectar_postgres(configuracao: ConfiguracaoBancos | None = None):
    configuracao = configuracao or carregar_configuracao()
    return psycopg.connect(
        host=configuracao.postgres_host,
        port=configuracao.postgres_port,
        dbname=configuracao.postgres_database,
        user=configuracao.postgres_user,
        password=configuracao.postgres_password,
        connect_timeout=5,
    )


def conectar_mongodb(configuracao: ConfiguracaoBancos | None = None) -> MongoClient:
    configuracao = configuracao or carregar_configuracao()
    client = MongoClient(configuracao.mongodb_uri, serverSelectionTimeoutMS=5_000)
    client.admin.command("ping")
    return client


def banco_mongodb(configuracao: ConfiguracaoBancos | None = None) -> Database:
    configuracao = configuracao or carregar_configuracao()
    return conectar_mongodb(configuracao)[configuracao.mongodb_database]
