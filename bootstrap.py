from __future__ import annotations

from config import ConfiguracaoAplicacao, carregar_configuracao
from infrastructure import GerenciadorConexoes
from repositories import RepositorioMongo, RepositorioOracle, RepositorioPostgres
from services import ServicoExtracao, ServicoPipeline, ServicoTransformacao


def criar_pipeline(configuracao: ConfiguracaoAplicacao | None = None) -> ServicoPipeline:
    """Monta o pipeline com os tres adaptadores de fontes operacionais."""
    conexoes = GerenciadorConexoes(configuracao or carregar_configuracao())
    extracao = ServicoExtracao(
        (
            RepositorioOracle(conexoes),
            RepositorioPostgres(conexoes),
            RepositorioMongo(conexoes),
        )
    )
    return ServicoPipeline(extracao, ServicoTransformacao())
