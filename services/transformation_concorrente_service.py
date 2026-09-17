from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from models import (
    FatoVendaConcorrente,
    LoteOlapConcorrente,
    LoteSilverConcorrente,
    VendaConcorrenteOrigem,
    VendaConcorrenteSilver,
)


class ServicoTransformacaoConcorrente:
    """Constroi Silver e Gold das vendas mensais da concorrente.

    Grao ano x quadrimestre apenas: a fonte nao traz quantidade, produto,
    cidade ou perfil de cliente (ver README.md).
    """

    def transformar_silver(
        self, vendas: Iterable[VendaConcorrenteOrigem]
    ) -> LoteSilverConcorrente:
        return LoteSilverConcorrente(
            vendas=tuple(
                VendaConcorrenteSilver(
                    ano=venda.ano,
                    quadrimestre=(venda.mes - 1) // 4 + 1,
                    mes=venda.mes,
                    valor_vendido=venda.valor,
                )
                for venda in vendas
            )
        )

    def transformar_gold(self, silver: LoteSilverConcorrente) -> LoteOlapConcorrente:
        agregados: dict[tuple[int, int], Decimal] = defaultdict(Decimal)
        for venda in silver.vendas:
            agregados[(venda.ano, venda.quadrimestre)] += venda.valor_vendido

        fatos = tuple(
            FatoVendaConcorrente(ano=ano, quadrimestre=quadrimestre, valor_vendido=valor)
            for (ano, quadrimestre), valor in sorted(agregados.items())
        )
        return LoteOlapConcorrente(fatos_vendas_concorrente=fatos)

    def transformar(self, vendas: Iterable[VendaConcorrenteOrigem]) -> LoteOlapConcorrente:
        """Atalho para o fluxo Bronze -> Silver -> Gold."""
        return self.transformar_gold(self.transformar_silver(vendas))
