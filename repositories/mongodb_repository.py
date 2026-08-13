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


class RepositorioMongo:
    """Adaptador dos documentos da loja Feira de Santana em MongoDB."""

    def __init__(self, conexoes: GerenciadorConexoes) -> None:
        self._conexoes = conexoes

    def extrair(self) -> DadosFonte:
        with self._conexoes.mongo() as banco:
            clientes = tuple(
                ClienteOrigem(
                    origem=FonteDados.FEIRA_DE_SANTANA,
                    id_cliente=str(documento["id_cliente"]),
                    nome=documento["nome"],
                    email=documento.get("email"),
                    telefone=documento.get("telefone"),
                    sexo=documento.get("sexo"),
                    estado_civil=documento.get("estado_civil"),
                    data_nascimento=para_data(documento.get("data_nascimento")),
                    data_cadastro=None,
                )
                for documento in banco.clientes.find({}, {"_id": 0}).sort("id_cliente", 1)
            )
            produtos = tuple(
                ProdutoOrigem(
                    origem=FonteDados.FEIRA_DE_SANTANA,
                    id_produto=str(documento["id_produto"]),
                    nome=documento["nome_produto"],
                    categoria=documento.get("categoria"),
                    preco=para_decimal(documento["preco"]),
                )
                for documento in banco.produtos.find({}, {"_id": 0}).sort("id_produto", 1)
            )
            vendas, itens_venda = self._extrair_pedidos(banco)

        return DadosFonte(
            origem=FonteDados.FEIRA_DE_SANTANA,
            clientes=clientes,
            produtos=produtos,
            vendas=vendas,
            itens_venda=itens_venda,
        )

    @staticmethod
    def _extrair_pedidos(banco) -> tuple[tuple[VendaOrigem, ...], tuple[ItemVendaOrigem, ...]]:
        vendas: list[VendaOrigem] = []
        itens_venda: list[ItemVendaOrigem] = []

        for pedido in banco.pedidos.find({}, {"_id": 0}).sort("id_pedido", 1):
            id_pedido = str(pedido["id_pedido"])
            data_pedido = para_data(pedido["data_pedido"])
            if data_pedido is None:
                raise ValueError(f"Pedido {id_pedido} sem data_pedido.")

            vendas.append(
                VendaOrigem(
                    origem=FonteDados.FEIRA_DE_SANTANA,
                    id_venda=id_pedido,
                    id_cliente=str(pedido["id_cliente"]),
                    data_venda=data_pedido,
                    valor_total=para_decimal(pedido["valor_total"]),
                )
            )

            for posicao, item in enumerate(pedido.get("itens", ()), start=1):
                itens_venda.append(
                    ItemVendaOrigem(
                        origem=FonteDados.FEIRA_DE_SANTANA,
                        id_item=f"{id_pedido}:{posicao}",
                        id_venda=id_pedido,
                        id_produto=str(item["id_produto"]),
                        quantidade=int(item["quantidade"]),
                        valor_unitario=para_decimal(item["preco_unitario"]),
                    )
                )

        return tuple(vendas), tuple(itens_venda)
