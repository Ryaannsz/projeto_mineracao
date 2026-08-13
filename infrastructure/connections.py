from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import oracledb
import psycopg
from pymongo import MongoClient

from config import ConfiguracaoAplicacao


class GerenciadorConexoes:
    """Centraliza a abertura e o fechamento das conexoes das fontes."""

    def __init__(self, configuracao: ConfiguracaoAplicacao) -> None:
        self._configuracao = configuracao

    @contextmanager
    def oracle(self) -> Iterator[Any]:
        configuracao = self._configuracao.oracle
        dsn = oracledb.makedsn(
            configuracao.host,
            configuracao.porta,
            service_name=configuracao.service_name,
        )
        conexao = oracledb.connect(
            user=configuracao.usuario,
            password=configuracao.senha,
            dsn=dsn,
        )
        try:
            yield conexao
        finally:
            conexao.close()

    @contextmanager
    def postgres(self) -> Iterator[Any]:
        configuracao = self._configuracao.postgres
        conexao = psycopg.connect(
            host=configuracao.host,
            port=configuracao.porta,
            dbname=configuracao.banco,
            user=configuracao.usuario,
            password=configuracao.senha,
            connect_timeout=5,
        )
        try:
            yield conexao
        finally:
            conexao.close()

    @contextmanager
    def mongo(self) -> Iterator[Any]:
        configuracao = self._configuracao.mongo
        cliente = MongoClient(configuracao.uri, serverSelectionTimeoutMS=5_000)
        try:
            cliente.admin.command("ping")
            yield cliente[configuracao.banco]
        finally:
            cliente.close()
