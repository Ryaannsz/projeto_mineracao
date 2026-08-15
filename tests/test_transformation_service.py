from datetime import date
from decimal import Decimal
from unittest import TestCase

from models import (
    ClienteOrigem,
    DadosFonte,
    FonteDados,
    ItemVendaOrigem,
    ProdutoOrigem,
    VendaOrigem,
)
from services import ServicoTransformacao


class ServicoTransformacaoTest(TestCase):
    def test_preserva_item_na_silver_e_agrega_na_gold(self) -> None:
        dados = DadosFonte(
            origem=FonteDados.SALVADOR,
            clientes=(
                ClienteOrigem(
                    origem=FonteDados.SALVADOR,
                    id_cliente="1",
                    nome="Ana Silva",
                    email=None,
                    telefone=None,
                    sexo="F",
                    estado_civil="U",
                    data_nascimento=None,
                    data_cadastro=None,
                ),
            ),
            produtos=(
                ProdutoOrigem(
                    origem=FonteDados.SALVADOR,
                    id_produto="10",
                    nome="Produto Teste",
                    categoria="Teste",
                    preco=Decimal("12.50"),
                ),
            ),
            vendas=(
                VendaOrigem(
                    origem=FonteDados.SALVADOR,
                    id_venda="100",
                    id_cliente="1",
                    data_venda=date(2025, 4, 15),
                    valor_total=None,
                ),
            ),
            itens_venda=(
                ItemVendaOrigem(
                    origem=FonteDados.SALVADOR,
                    id_item="1000",
                    id_venda="100",
                    id_produto="10",
                    quantidade=2,
                    valor_unitario=Decimal("12.50"),
                ),
                ItemVendaOrigem(
                    origem=FonteDados.SALVADOR,
                    id_item="1001",
                    id_venda="100",
                    id_produto="10",
                    quantidade=3,
                    valor_unitario=Decimal("12.50"),
                ),
            ),
        )

        transformacao = ServicoTransformacao()
        silver = transformacao.transformar_silver((dados,))
        gold = transformacao.transformar_gold(silver)

        self.assertEqual(silver.quantidades(), {"vendas_silver": 2})
        self.assertEqual(silver.vendas[0].cidade, "Salvador")
        self.assertEqual(silver.vendas[0].quadrimestre, 1)
        self.assertEqual(silver.vendas[0].estado_civil, "Uniao Estavel")
        self.assertEqual(gold.quantidades()["fato_vendas"], 1)
        self.assertEqual(gold.fatos_vendas[0].quantidade_vendida, 5)
        self.assertEqual(gold.fatos_vendas[0].valor_vendido, Decimal("62.50"))

    def test_substitui_estado_civil_ausente_por_nao_informado(self) -> None:
        dados = DadosFonte(
            origem=FonteDados.ITABUNA,
            clientes=(
                ClienteOrigem(
                    origem=FonteDados.ITABUNA,
                    id_cliente="1",
                    nome="Ana Silva",
                    email=None,
                    telefone=None,
                    sexo=None,
                    estado_civil=None,
                    data_nascimento=None,
                    data_cadastro=None,
                ),
            ),
            produtos=(
                ProdutoOrigem(
                    origem=FonteDados.ITABUNA,
                    id_produto="1",
                    nome="Produto",
                    categoria=None,
                    preco=Decimal("1"),
                ),
            ),
            vendas=(
                VendaOrigem(
                    origem=FonteDados.ITABUNA,
                    id_venda="1",
                    id_cliente="1",
                    data_venda=date(2024, 12, 1),
                    valor_total=None,
                ),
            ),
            itens_venda=(
                ItemVendaOrigem(
                    origem=FonteDados.ITABUNA,
                    id_item="1",
                    id_venda="1",
                    id_produto="1",
                    quantidade=1,
                    valor_unitario=Decimal("1"),
                ),
            ),
        )

        silver = ServicoTransformacao().transformar_silver((dados,))

        self.assertEqual(silver.vendas[0].cidade, "Itabuna")
        self.assertEqual(silver.vendas[0].quadrimestre, 3)
        self.assertEqual(silver.vendas[0].categoria, "Sem categoria")
        self.assertEqual(silver.vendas[0].estado_civil, "Nao informado")
