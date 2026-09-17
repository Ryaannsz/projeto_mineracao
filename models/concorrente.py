from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class VendaConcorrenteOrigem:
    """Linha mensal bruta da planilha de vendas da concorrente."""

    ano: int
    mes: int
    valor: Decimal


@dataclass(frozen=True, slots=True)
class VendaConcorrenteSilver:
    """Venda mensal da concorrente com periodo padronizado (ano/quadrimestre)."""

    ano: int
    quadrimestre: int
    mes: int
    valor_vendido: Decimal


@dataclass(frozen=True, slots=True)
class LoteSilverConcorrente:
    vendas: tuple[VendaConcorrenteSilver, ...]

    def quantidades(self) -> dict[str, int]:
        return {"vendas_concorrente_silver": len(self.vendas)}


@dataclass(frozen=True, slots=True)
class FatoVendaConcorrente:
    """Vendas da concorrente agregadas no grao ano x quadrimestre.

    Sem quantidade, produto, cidade ou estado civil: a planilha fonte so
    fornece valor mensal agregado (ver README.md).
    """

    ano: int
    quadrimestre: int
    valor_vendido: Decimal


@dataclass(frozen=True, slots=True)
class LoteOlapConcorrente:
    fatos_vendas_concorrente: tuple[FatoVendaConcorrente, ...]

    def quantidades(self) -> dict[str, int]:
        return {"fato_vendas_concorrente": len(self.fatos_vendas_concorrente)}
