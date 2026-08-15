from __future__ import annotations

from models import LoteOlap, LoteSilver
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
        return self.preparar_gold(self.preparar_silver())

    def preparar_silver(self) -> LoteSilver:
        """Extrai Bronze e entrega vendas padronizadas, ainda no grao de item."""
        return self._transformacao.transformar_silver(self._extracao.extrair())

    def preparar_gold(self, silver: LoteSilver) -> LoteOlap:
        """Agrega a Silver no grao analitico da estrela."""
        return self._transformacao.transformar_gold(silver)

    def executar(self, repositorio_olap: RepositorioOlap) -> LoteOlap:
        lote = self.preparar_lote()
        repositorio_olap.carregar(lote)
        return lote
