from decimal import Decimal
from unittest import TestCase

from models import VendaConcorrenteOrigem
from services import ServicoTransformacaoConcorrente


class ServicoTransformacaoConcorrenteTest(TestCase):
    def test_agrega_meses_por_quadrimestre(self) -> None:
        vendas = (
            VendaConcorrenteOrigem(ano=2024, mes=1, valor=Decimal("185000")),
            VendaConcorrenteOrigem(ano=2024, mes=2, valor=Decimal("178000")),
            VendaConcorrenteOrigem(ano=2024, mes=4, valor=Decimal("205000")),
            VendaConcorrenteOrigem(ano=2024, mes=5, valor=Decimal("198000")),
        )

        transformacao = ServicoTransformacaoConcorrente()
        silver = transformacao.transformar_silver(vendas)
        gold = transformacao.transformar_gold(silver)

        self.assertEqual(silver.quantidades(), {"vendas_concorrente_silver": 4})
        self.assertEqual(silver.vendas[0].quadrimestre, 1)
        self.assertEqual(silver.vendas[2].quadrimestre, 1)
        self.assertEqual(silver.vendas[3].quadrimestre, 2)

        self.assertEqual(gold.quantidades(), {"fato_vendas_concorrente": 2})
        primeiro_quadrimestre = next(
            fato for fato in gold.fatos_vendas_concorrente if fato.quadrimestre == 1
        )
        self.assertEqual(primeiro_quadrimestre.valor_vendido, Decimal("568000"))

    def test_atalho_transformar_equivale_a_silver_mais_gold(self) -> None:
        vendas = (VendaConcorrenteOrigem(ano=2025, mes=12, valor=Decimal("215000")),)

        transformacao = ServicoTransformacaoConcorrente()
        gold = transformacao.transformar(vendas)

        self.assertEqual(len(gold.fatos_vendas_concorrente), 1)
        fato = gold.fatos_vendas_concorrente[0]
        self.assertEqual((fato.ano, fato.quadrimestre), (2025, 3))
        self.assertEqual(fato.valor_vendido, Decimal("215000"))
