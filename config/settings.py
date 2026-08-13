from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote_plus

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class ConfiguracaoOracle:
    host: str
    porta: int
    service_name: str
    usuario: str
    senha: str


@dataclass(frozen=True, slots=True)
class ConfiguracaoPostgres:
    host: str
    porta: int
    banco: str
    usuario: str
    senha: str


@dataclass(frozen=True, slots=True)
class ConfiguracaoMongo:
    uri: str
    banco: str


@dataclass(frozen=True, slots=True)
class ConfiguracaoAplicacao:
    oracle: ConfiguracaoOracle
    postgres: ConfiguracaoPostgres
    mongo: ConfiguracaoMongo


def carregar_configuracao() -> ConfiguracaoAplicacao:
    """Carrega as configuracoes locais ou as fornecidas pelo ambiente."""
    load_dotenv()

    mongo_usuario = quote_plus(os.getenv("MONGO_ROOT_USER", "root"))
    mongo_senha = quote_plus(os.getenv("MONGO_ROOT_PASSWORD", "Mongo123"))
    mongo_host = os.getenv("MONGODB_HOST", "localhost")
    mongo_porta = os.getenv("MONGO_PORT", "27017")

    return ConfiguracaoAplicacao(
        oracle=ConfiguracaoOracle(
            host=os.getenv("ORACLE_HOST", "localhost"),
            porta=int(os.getenv("ORACLE_PORT", "1521")),
            service_name=os.getenv("ORACLE_SERVICE", "FREEPDB1"),
            usuario=os.getenv("ORACLE_USER", "petshop"),
            senha=os.getenv("ORACLE_USER_PASSWORD", "Petshop123"),
        ),
        postgres=ConfiguracaoPostgres(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            porta=int(os.getenv("POSTGRES_PORT", "5432")),
            banco=os.getenv("POSTGRES_DB", "petshop_itabuna"),
            usuario=os.getenv("POSTGRES_USER", "petshop"),
            senha=os.getenv("POSTGRES_PASSWORD", "Postgres123"),
        ),
        mongo=ConfiguracaoMongo(
            uri=os.getenv(
                "MONGODB_URI",
                f"mongodb://{mongo_usuario}:{mongo_senha}@{mongo_host}:{mongo_porta}/?authSource=admin",
            ),
            banco=os.getenv("MONGO_DATABASE", "petshop_feira"),
        ),
    )
