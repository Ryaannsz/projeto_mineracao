from __future__ import annotations

from typing import Protocol

from models import LoteOlapConcorrente, VendaConcorrenteOrigem

from .transformation_concorrente_service import ServicoTransformacaoConcorrente


class RepositorioConcorrenteOlap(Protocol):
    def carregar_concorrente(self, lote: LoteOlapConcorrente) -> None: ...


class RepositorioPlanilhaConcorrenteFonte(Protocol):
    def extrair(self) -> tuple[VendaConcorrenteOrigem, ...]: ...


class ServicoPipelineConcorrente:
    """Orquestra extracao, transformacao e carga das vendas da concorrente."""

    def __init__(
        self,
        extracao: RepositorioPlanilhaConcorrenteFonte,
        transformacao: ServicoTransformacaoConcorrente,
    ) -> None:
        self._extracao = extracao
        self._transformacao = transformacao

    def preparar_lote(self) -> LoteOlapConcorrente:
        return self._transformacao.transformar(self._extracao.extrair())

    def executar(self, repositorio_olap: RepositorioConcorrenteOlap) -> LoteOlapConcorrente:
        lote = self.preparar_lote()
        repositorio_olap.carregar_concorrente(lote)
        return lote
