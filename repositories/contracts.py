from __future__ import annotations

from typing import Protocol

from models import DadosFonte, LoteOlap


class RepositorioFonte(Protocol):
    """Contrato de qualquer adaptador que extrai uma fonte operacional."""

    def extrair(self) -> DadosFonte: ...


class RepositorioOlap(Protocol):
    """Contrato a ser implementado quando a tecnologia do OLAP for definida."""

    def carregar(self, lote: LoteOlap) -> None: ...
