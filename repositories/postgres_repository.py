from __future__ import annotations

from infrastructure import GerenciadorConexoes
from models import (
    AtendimentoServicoOrigem,
    ClienteOrigem,
    DadosFonte,
    FonteDados,
    ItemVendaOrigem,
    ProdutoOrigem,
    ServicoOrigem,
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
    SELECT id_produto, nome, categoria, preco
    FROM produtos
    ORDER BY id_produto
"""

SQL_VENDAS = """
    SELECT id_venda, id_cliente, data_venda, valor_total
    FROM vendas
    ORDER BY id_venda
"""

SQL_ITENS_VENDA = """
    SELECT id_item, id_venda, id_produto, quantidade, valor_unitario
    FROM itens_venda
    ORDER BY id_item
"""

SQL_SERVICOS = """
    SELECT id_servico, descricao, valor
    FROM servicos
    ORDER BY id_servico
"""

SQL_ATENDIMENTOS = """
    SELECT id_atendimento, id_cliente, id_servico, data_atendimento, valor_cobrado
    FROM atendimento_servico
    ORDER BY id_atendimento
"""


class RepositorioPostgres:
    """Adaptador da loja Itabuna hospedada em PostgreSQL."""

    def __init__(self, conexoes: GerenciadorConexoes) -> None:
        self._conexoes = conexoes

    def extrair(self) -> DadosFonte:
        with self._conexoes.postgres() as conexao:
            with conexao.cursor() as cursor:
                clientes = self._listar_clientes(cursor)
                produtos = self._listar_produtos(cursor)
                vendas = self._listar_vendas(cursor)
                itens_venda = self._listar_itens_venda(cursor)
                servicos = self._listar_servicos(cursor)
                atendimentos = self._listar_atendimentos(cursor)

        return DadosFonte(
            origem=FonteDados.ITABUNA,
            clientes=clientes,
            produtos=produtos,
            vendas=vendas,
            itens_venda=itens_venda,
            servicos=servicos,
            atendimentos_servico=atendimentos,
        )

    @staticmethod
    def _listar_clientes(cursor) -> tuple[ClienteOrigem, ...]:
        cursor.execute(SQL_CLIENTES)
        return tuple(
            ClienteOrigem(
                origem=FonteDados.ITABUNA,
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
                origem=FonteDados.ITABUNA,
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
                origem=FonteDados.ITABUNA,
                id_venda=str(id_venda),
                id_cliente=str(id_cliente),
                data_venda=para_data(data_venda),
                valor_total=para_decimal(valor_total),
            )
            for id_venda, id_cliente, data_venda, valor_total in cursor.fetchall()
        )

    @staticmethod
    def _listar_itens_venda(cursor) -> tuple[ItemVendaOrigem, ...]:
        cursor.execute(SQL_ITENS_VENDA)
        return tuple(
            ItemVendaOrigem(
                origem=FonteDados.ITABUNA,
                id_item=str(id_item),
                id_venda=str(id_venda),
                id_produto=str(id_produto),
                quantidade=int(quantidade),
                valor_unitario=para_decimal(valor_unitario),
            )
            for id_item, id_venda, id_produto, quantidade, valor_unitario in cursor.fetchall()
        )

    @staticmethod
    def _listar_servicos(cursor) -> tuple[ServicoOrigem, ...]:
        cursor.execute(SQL_SERVICOS)
        return tuple(
            ServicoOrigem(
                origem=FonteDados.ITABUNA,
                id_servico=str(id_servico),
                descricao=descricao,
                valor=para_decimal(valor),
            )
            for id_servico, descricao, valor in cursor.fetchall()
        )

    @staticmethod
    def _listar_atendimentos(cursor) -> tuple[AtendimentoServicoOrigem, ...]:
        cursor.execute(SQL_ATENDIMENTOS)
        return tuple(
            AtendimentoServicoOrigem(
                origem=FonteDados.ITABUNA,
                id_atendimento=str(id_atendimento),
                id_cliente=str(id_cliente),
                id_servico=str(id_servico),
                data_atendimento=para_data(data_atendimento),
                valor_cobrado=para_decimal(valor_cobrado),
            )
            for (
                id_atendimento,
                id_cliente,
                id_servico,
                data_atendimento,
                valor_cobrado,
            ) in cursor.fetchall()
        )
