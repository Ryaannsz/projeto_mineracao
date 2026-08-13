from __future__ import annotations

from models import LoteOlap
from repositories.contracts import RepositorioOlap

from .extraction_service import ServicoExtracao
from .transformation_service import ServicoTransformacao


class ServicoPipeline:
    """Orquestra as etapas de extracao, transformacao e carga."""

    def __init__(
        self,
        extracao: ServicoExtracao,
        transformacao: ServicoTransformacao,
    ) -> None:
        self._extracao = extracao
        self._transformacao = transformacao

    def preparar_lote(self) -> LoteOlap:
        fontes = self._extracao.extrair()
        return self._transformacao.transformar(fontes)

    def executar(self, repositorio_olap: RepositorioOlap) -> LoteOlap:
        lote = self.preparar_lote()
        repositorio_olap.carregar(lote)
        return lote
