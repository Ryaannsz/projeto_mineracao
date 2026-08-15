from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DimensaoTempo:
    chave_natural: str
    ano: int
    quadrimestre: int


@dataclass(frozen=True, slots=True)
class DimensaoProduto:
    chave_natural: str
    nome: str
    categoria: str


@dataclass(frozen=True, slots=True)
class DimensaoCidade:
    chave_natural: str
    cidade: str


@dataclass(frozen=True, slots=True)
class DimensaoEstadoCivil:
    chave_natural: str
    descricao: str


@dataclass(frozen=True, slots=True)
class FatoVenda:
    chave_tempo_natural: str
    chave_produto_natural: str
    chave_cidade_natural: str
    chave_estado_civil_natural: str
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
