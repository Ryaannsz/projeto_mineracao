from __future__ import annotations

from infrastructure import GerenciadorConexoes
from models import (
    ClienteOrigem,
    DadosFonte,
    FonteDados,
    ItemVendaOrigem,
    ProdutoOrigem,
    VendaOrigem,
)

from .mappers import para_data, para_decimal


SQL_CLIENTES = """
    SELECT id_cliente, nome, email, telefone, sexo, estado_civil,
           data_nascimento, data_cadastro
    FROM clientes
    ORDER BY id_cliente
"""

SQL_PRODUTOS = """
    SELECT p.id_produto, p.nome, c.nome_categoria, p.preco
    FROM produtos p
    LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
    ORDER BY p.id_produto
"""

SQL_VENDAS = """
    SELECT id_venda, id_cliente, data_venda
    FROM vendas
    ORDER BY id_venda
"""

SQL_ITENS_VENDA = """
    SELECT id_item, id_venda, id_produto, quantidade, valor_unitario
    FROM itens_venda
    ORDER BY id_item
"""


class RepositorioOracle:
    """Adaptador da loja Salvador hospedada em Oracle."""

    def __init__(self, conexoes: GerenciadorConexoes) -> None:
        self._conexoes = conexoes

    def extrair(self) -> DadosFonte:
        with self._conexoes.oracle() as conexao:
            with conexao.cursor() as cursor:
                clientes = self._listar_clientes(cursor)
                produtos = self._listar_produtos(cursor)
                vendas = self._listar_vendas(cursor)
                itens_venda = self._listar_itens_venda(cursor)

        return DadosFonte(
            origem=FonteDados.SALVADOR,
            clientes=clientes,
            produtos=produtos,
            vendas=vendas,
            itens_venda=itens_venda,
        )

    @staticmethod
    def _listar_clientes(cursor) -> tuple[ClienteOrigem, ...]:
        cursor.execute(SQL_CLIENTES)
        return tuple(
            ClienteOrigem(
                origem=FonteDados.SALVADOR,
                id_cliente=str(id_cliente),
                nome=nome,
                email=email,
                telefone=telefone,
                sexo=sexo,
                estado_civil=estado_civil,
                data_nascimento=para_data(data_nascimento),
                data_cadastro=para_data(data_cadastro),
            )
            for (
                id_cliente,
                nome,
                email,
                telefone,
                sexo,
                estado_civil,
                data_nascimento,
                data_cadastro,
            ) in cursor.fetchall()
        )

    @staticmethod
    def _listar_produtos(cursor) -> tuple[ProdutoOrigem, ...]:
        cursor.execute(SQL_PRODUTOS)
        return tuple(
            ProdutoOrigem(
                origem=FonteDados.SALVADOR,
                id_produto=str(id_produto),
                nome=nome,
                categoria=categoria,
                preco=para_decimal(preco),
            )
            for id_produto, nome, categoria, preco in cursor.fetchall()
        )

    @staticmethod
    def _listar_vendas(cursor) -> tuple[VendaOrigem, ...]:
        cursor.execute(SQL_VENDAS)
        return tuple(
            VendaOrigem(
                origem=FonteDados.SALVADOR,
                id_venda=str(id_venda),
                id_cliente=str(id_cliente),
                data_venda=para_data(data_venda),
                valor_total=None,
            )
            for id_venda, id_cliente, data_venda in cursor.fetchall()
        )

    @staticmethod
    def _listar_itens_venda(cursor) -> tuple[ItemVendaOrigem, ...]:
        cursor.execute(SQL_ITENS_VENDA)
        return tuple(
            ItemVendaOrigem(
                origem=FonteDados.SALVADOR,
                id_item=str(id_item),
                id_venda=str(id_venda),
                id_produto=str(id_produto),
                quantidade=int(quantidade),
                valor_unitario=para_decimal(valor_unitario),
            )
            for id_item, id_venda, id_produto, quantidade, valor_unitario in cursor.fetchall()
        )
