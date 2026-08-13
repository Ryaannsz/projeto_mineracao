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
    def test_cria_dimensoes_e_fato_no_grao_do_item(self) -> None:
        dados = DadosFonte(
            origem=FonteDados.SALVADOR,
            clientes=(
                ClienteOrigem(
                    origem=FonteDados.SALVADOR,
                    id_cliente="1",
                    nome=" Ana   Silva ",
                    email="ANA@EXAMPLE.COM",
                    telefone=None,
                    sexo="Feminino",
                    estado_civil="U",
                    data_nascimento=date(1990, 1, 1),
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
                    data_venda=date(2025, 1, 15),
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
            ),
        )

        lote = ServicoTransformacao().transformar((dados,))

        self.assertEqual(lote.quantidades()["dimensao_clientes"], 1)
        self.assertEqual(lote.quantidades()["dimensao_datas"], 1)
        self.assertEqual(lote.quantidades()["fato_itens_venda"], 1)
        self.assertEqual(lote.clientes[0].nome, "Ana Silva")
        self.assertEqual(lote.clientes[0].email, "ana@example.com")
        self.assertEqual(lote.clientes[0].estado_civil, "Uniao Estavel")
        self.assertEqual(lote.fatos_itens_venda[0].valor_total_item, Decimal("25.00"))
        self.assertEqual(lote.fatos_itens_venda[0].chave_data, 20250115)
