from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DimensaoTempo:
    ano: int
    quadrimestre: int


@dataclass(frozen=True, slots=True)
class DimensaoProduto:
    nome: str
    categoria: str


@dataclass(frozen=True, slots=True)
class DimensaoCidade:
    cidade: str


@dataclass(frozen=True, slots=True)
class DimensaoEstadoCivil:
    descricao: str


@dataclass(frozen=True, slots=True)
class FatoVenda:
    ano: int
    quadrimestre: int
    produto: str
    categoria: str
    cidade: str
    estado_civil: str
    quantidade_vendida: int
    valor_vendido: Decimal


@dataclass(frozen=True, slots=True)
class LoteOlap:
    tempos: tuple[DimensaoTempo, ...]
    produtos: tuple[DimensaoProduto, ...]
    cidades: tuple[DimensaoCidade, ...]
    estados_civis: tuple[DimensaoEstadoCivil, ...]
    fatos_vendas: tuple[FatoVenda, ...]

    def quantidades(self) -> dict[str, int]:
        return {
            "dimensao_tempos": len(self.tempos),
            "dimensao_produtos": len(self.produtos),
            "dimensao_cidades": len(self.cidades),
            "dimensao_estados_civis": len(self.estados_civis),
            "fato_vendas": len(self.fatos_vendas),
        }
