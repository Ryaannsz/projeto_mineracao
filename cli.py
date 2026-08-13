from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from config import carregar_configuracao
from infrastructure import GerenciadorConexoes

from bootstrap import criar_pipeline


def main(argumentos: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ferramentas do ETL do Pet Shop Nosso Aumigo.")
    subcomandos = parser.add_subparsers(dest="comando", required=True)
    subcomandos.add_parser("verificar-conexoes", help="Valida as tres fontes operacionais.")
    subcomandos.add_parser("preparar-lote", help="Extrai e transforma dados sem carregar um OLAP.")
    args = parser.parse_args(argumentos)

    if args.comando == "verificar-conexoes":
        _verificar_conexoes()
    elif args.comando == "preparar-lote":
        lote = criar_pipeline().preparar_lote()
        print(json.dumps(lote.quantidades(), indent=2, sort_keys=True))

    return 0


def _verificar_conexoes() -> None:
    conexoes = GerenciadorConexoes(carregar_configuracao())

    with conexoes.oracle() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            print(f"Oracle: conectado, {cursor.fetchone()[0]} clientes em Salvador")

    with conexoes.postgres() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            print(f"PostgreSQL: conectado, {cursor.fetchone()[0]} clientes em Itabuna")

    with conexoes.mongo() as banco:
        print(f"MongoDB: conectado, {banco.clientes.count_documents({})} clientes em Feira de Santana")
