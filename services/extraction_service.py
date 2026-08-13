from __future__ import annotations

from collections.abc import Iterable

from models import DadosFonte
from repositories.contracts import RepositorioFonte


class ServicoExtracao:
    def __init__(self, repositorios: Iterable[RepositorioFonte]) -> None:
        self._repositorios = tuple(repositorios)

    def extrair(self) -> tuple[DadosFonte, ...]:
        return tuple(repositorio.extrair() for repositorio in self._repositorios)
