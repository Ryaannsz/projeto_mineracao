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
                            ids_tempo[(fato.ano, fato.quadrimestre)],
                            ids_produto[(fato.produto, fato.categoria)],
                            ids_cidade[fato.cidade],
                            ids_estado_civil[fato.estado_civil],
                            fato.quantidade_vendida,
                            fato.valor_vendido,
                        )
                        for fato in lote.fatos_vendas
                    ],
                )
            conexao.commit()

    @staticmethod
    def _inserir_tempos(cursor, lote: LoteOlap) -> dict[tuple[int, int], int]:
        cursor.executemany(
            "INSERT INTO dim_tempo (ano, quadrimestre) VALUES (%s, %s)",
            [(item.ano, item.quadrimestre) for item in lote.tempos],
        )
        cursor.execute("SELECT ano, quadrimestre, id_tempo FROM dim_tempo")
        return {(ano, quadrimestre): id_tempo for ano, quadrimestre, id_tempo in cursor.fetchall()}

    @staticmethod
    def _inserir_produtos(cursor, lote: LoteOlap) -> dict[tuple[str, str], int]:
        cursor.executemany(
            "INSERT INTO dim_produto (nome, categoria) VALUES (%s, %s)",
            [(item.nome, item.categoria) for item in lote.produtos],
        )
        cursor.execute("SELECT nome, categoria, id_produto FROM dim_produto")
        return {(nome, categoria): id_produto for nome, categoria, id_produto in cursor.fetchall()}

    @staticmethod
    def _inserir_cidades(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_cidade (cidade) VALUES (%s)",
            [(item.cidade,) for item in lote.cidades],
        )
        cursor.execute("SELECT cidade, id_cidade FROM dim_cidade")
        return dict(cursor.fetchall())

    @staticmethod
    def _inserir_estados_civis(cursor, lote: LoteOlap) -> dict[str, int]:
        cursor.executemany(
            "INSERT INTO dim_estado_civil (descricao) VALUES (%s)",
            [(item.descricao,) for item in lote.estados_civis],
        )
        cursor.execute("SELECT descricao, id_estado_civil FROM dim_estado_civil")
        return dict(cursor.fetchall())
