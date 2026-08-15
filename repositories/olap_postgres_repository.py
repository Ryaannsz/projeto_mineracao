from __future__ import annotations

from models import LoteOlap

from infrastructure import GerenciadorConexoes


class RepositorioOlapPostgres:
    """Carrega a camada Gold no esquema estrela PostgreSQL."""

    def __init__(self, conexoes: GerenciadorConexoes) -> None:
        self._conexoes = conexoes

    def carregar(self, lote: LoteOlap) -> None:
        with self._conexoes.olap() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "TRUNCATE fato_vendas, dim_tempo, dim_produto, dim_cidade, "
                    "dim_estado_civil RESTART IDENTITY CASCADE"
                )
                ids_tempo = self._inserir_tempos(cursor, lote)
                ids_produto = self._inserir_produtos(cursor, lote)
                ids_cidade = self._inserir_cidades(cursor, lote)
                ids_estado_civil = self._inserir_estados_civis(cursor, lote)
                cursor.executemany(
                    """
                    INSERT INTO fato_vendas (
                        id_tempo, id_produto, id_cidade, id_estado_civil,
                        quantidade_vendida, valor_vendido
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            ids_tempo[fato.chave_tempo_natural],
                            ids_produto[fato.chave_produto_natural],
                            ids_cidade[fato.chave_cidade_natural],
                            ids_estado_civil[fato.chave_estado_civil_natural],
                            fato.quantidade_vendida,
                            fato.valor_vendido,
                        )
                        for fato in lote.fatos_vendas
                    ],
                )
            conexao.commit()

    @staticmethod
    def _inserir_tempos(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_tempo (chave_natural, ano, quadrimestre) VALUES (%s, %s, %s)",
            [(item.chave_natural, item.ano, item.quadrimestre) for item in lote.tempos],
        )
        return RepositorioOlapPostgres._mapear_ids(cursor, "dim_tempo")

    @staticmethod
    def _inserir_produtos(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_produto (chave_natural, nome, categoria) VALUES (%s, %s, %s)",
            [(item.chave_natural, item.nome, item.categoria) for item in lote.produtos],
        )
        return RepositorioOlapPostgres._mapear_ids(cursor, "dim_produto")

    @staticmethod
    def _inserir_cidades(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_cidade (chave_natural, cidade) VALUES (%s, %s)",
            [(item.chave_natural, item.cidade) for item in lote.cidades],
        )
        return RepositorioOlapPostgres._mapear_ids(cursor, "dim_cidade")

    @staticmethod
    def _inserir_estados_civis(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_estado_civil (chave_natural, descricao) VALUES (%s, %s)",
            [(item.chave_natural, item.descricao) for item in lote.estados_civis],
        )
        return RepositorioOlapPostgres._mapear_ids(cursor, "dim_estado_civil")

    @staticmethod
    def _mapear_ids(cursor, tabela: str) -> dict[str, int]:
        cursor.execute(f"SELECT chave_natural, id_{tabela.removeprefix('dim_')} FROM {tabela}")
        return dict(cursor.fetchall())
