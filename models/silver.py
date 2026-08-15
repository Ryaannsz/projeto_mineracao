from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .source import FonteDados


@dataclass(frozen=True, slots=True)
class VendaSilver:
    """Venda propria no grao de um item, com campos padronizados."""

    origem: FonteDados
    codigo_venda_origem: str
    cidade: str
    data_venda: date
    ano: int
    quadrimestre: int
    produto: str
    categoria: str
    estado_civil: str
    quantidade: int
    valor_vendido: Decimal


@dataclass(frozen=True, slots=True)
class LoteSilver:
    vendas: tuple[VendaSilver, ...]

    def quantidades(self) -> dict[str, int]:
        return {"vendas_silver": len(self.vendas)}
