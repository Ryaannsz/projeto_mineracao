from __future__ import annotations

from config import ConfiguracaoAplicacao, carregar_configuracao
from infrastructure import GerenciadorConexoes
from repositories import (
    RepositorioMongo,
    RepositorioOlapPostgres,
    RepositorioOracle,
    RepositorioPlanilhaConcorrente,
    RepositorioPostgres,
)
from services import (
    ServicoExtracao,
    ServicoPipeline,
    ServicoPipelineConcorrente,
    ServicoTransformacao,
    ServicoTransformacaoConcorrente,
)


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


def criar_pipeline_concorrente(
    configuracao: ConfiguracaoAplicacao | None = None,
) -> ServicoPipelineConcorrente:
    """Monta o pipeline da planilha de vendas da concorrente."""
    configuracao = configuracao or carregar_configuracao()
    extracao = RepositorioPlanilhaConcorrente(configuracao.planilha_concorrente)
    return ServicoPipelineConcorrente(extracao, ServicoTransformacaoConcorrente())


def criar_repositorio_olap(
    configuracao: ConfiguracaoAplicacao | None = None,
) -> RepositorioOlapPostgres:
    """Monta o destino PostgreSQL da camada Gold."""
    return RepositorioOlapPostgres(GerenciadorConexoes(configuracao or carregar_configuracao()))
