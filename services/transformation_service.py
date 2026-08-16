from __future__ import annotations

import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from models import (
    DadosFonte,
    DimensaoCidade,
    DimensaoEstadoCivil,
    DimensaoProduto,
    DimensaoTempo,
    FatoVenda,
    FonteDados,
    LoteOlap,
    LoteSilver,
    VendaSilver,
    chave_origem,
)


_CIDADE_POR_FONTE = {
    FonteDados.SALVADOR: "Salvador",
    FonteDados.ITABUNA: "Itabuna",
    FonteDados.FEIRA_DE_SANTANA: "Feira de Santana",
}


class ServicoTransformacao:
    """Constroi as camadas Silver e Gold das vendas de produtos proprias."""

    def transformar_silver(self, fontes: Iterable[DadosFonte]) -> LoteSilver:
        vendas_silver: list[VendaSilver] = []
        for dados in fontes:
            vendas_por_chave = {
                chave_origem(dados.origem, venda.id_venda): venda for venda in dados.vendas
            }
            clientes_por_chave = {
                chave_origem(dados.origem, cliente.id_cliente): cliente
                for cliente in dados.clientes
            }
            produtos_por_chave = {
                chave_origem(dados.origem, produto.id_produto): produto
                for produto in dados.produtos
            }

            for item in dados.itens_venda:
                venda = vendas_por_chave.get(chave_origem(dados.origem, item.id_venda))
                if venda is None:
                    raise ValueError(f"Item {item.id_item} sem venda correspondente.")
                cliente = clientes_por_chave.get(chave_origem(dados.origem, venda.id_cliente))
                if cliente is None:
                    raise ValueError(f"Venda {venda.id_venda} sem cliente correspondente.")
                produto = produtos_por_chave.get(chave_origem(dados.origem, item.id_produto))
                if produto is None:
                    raise ValueError(f"Item {item.id_item} sem produto correspondente.")

                data_venda = venda.data_venda
                vendas_silver.append(
                    VendaSilver(
                        origem=dados.origem,
                        codigo_venda_origem=venda.id_venda,
                        cidade=_CIDADE_POR_FONTE[dados.origem],
                        data_venda=data_venda,
                        ano=data_venda.year,
                        quadrimestre=(data_venda.month - 1) // 4 + 1,
                        produto=_texto_obrigatorio(produto.nome),
                        categoria=_normalizar_texto(produto.categoria) or "Sem categoria",
                        estado_civil=_normalizar_estado_civil(cliente.estado_civil),
                        quantidade=item.quantidade,
                        valor_vendido=item.quantidade * item.valor_unitario,
                    )
                )
        return LoteSilver(vendas=tuple(vendas_silver))

    def transformar_gold(self, silver: LoteSilver) -> LoteOlap:
        tempos: dict[tuple[int, int], DimensaoTempo] = {}
        produtos: dict[tuple[str, str], DimensaoProduto] = {}
        cidades: dict[str, DimensaoCidade] = {}
        estados_civis: dict[str, DimensaoEstadoCivil] = {}
        agregados: dict[tuple[int, int, str, str, str, str], list] = defaultdict(
            lambda: [0, Decimal("0")]
        )

        for venda in silver.vendas:
            tempos[(venda.ano, venda.quadrimestre)] = DimensaoTempo(
                venda.ano, venda.quadrimestre
            )
            produto_padronizado = (_chave_texto(venda.produto), _chave_texto(venda.categoria))
            produtos.setdefault(
                produto_padronizado,
                DimensaoProduto(venda.produto, venda.categoria),
            )
            cidades[venda.cidade] = DimensaoCidade(venda.cidade)
            estados_civis[venda.estado_civil] = DimensaoEstadoCivil(venda.estado_civil)
            agregado = agregados[
                (
                    venda.ano,
                    venda.quadrimestre,
                    produto_padronizado[0],
                    produto_padronizado[1],
                    venda.cidade,
                    venda.estado_civil,
                )
            ]
            agregado[0] += venda.quantidade
            agregado[1] += venda.valor_vendido

        fatos = tuple(
            FatoVenda(
                ano=chaves[0],
                quadrimestre=chaves[1],
                produto=produtos[(chaves[2], chaves[3])].nome,
                categoria=produtos[(chaves[2], chaves[3])].categoria,
                cidade=chaves[4],
                estado_civil=chaves[5],
                quantidade_vendida=valores[0],
                valor_vendido=valores[1],
            )
            for chaves, valores in sorted(agregados.items())
        )
        return LoteOlap(
            tempos=tuple(sorted(tempos.values(), key=lambda item: (item.ano, item.quadrimestre))),
            produtos=tuple(sorted(produtos.values(), key=lambda item: (item.nome, item.categoria))),
            cidades=tuple(sorted(cidades.values(), key=lambda item: item.cidade)),
            estados_civis=tuple(sorted(estados_civis.values(), key=lambda item: item.descricao)),
            fatos_vendas=fatos,
        )

    def transformar(self, fontes: Iterable[DadosFonte]) -> LoteOlap:
        """Atalho para o fluxo Bronze -> Silver -> Gold."""
        return self.transformar_gold(self.transformar_silver(fontes))


def _texto_obrigatorio(valor: str) -> str:
    texto = _normalizar_texto(valor)
    if texto is None:
        raise ValueError("Campo textual obrigatorio vazio.")
    return texto


def _normalizar_texto(valor: str | None) -> str | None:
    if valor is None:
        return None
    texto = " ".join(str(valor).split())
    return texto or None


def _normalizar_estado_civil(valor: str | None) -> str:
    chave = _chave_texto(valor)
    valores = {
        "s": "Solteiro",
        "solteiro": "Solteiro",
        "c": "Casado",
        "casado": "Casado",
        "d": "Divorciado",
        "divorciado": "Divorciado",
        "v": "Viuvo",
        "viuvo": "Viuvo",
        "u": "Uniao Estavel",
        "uniao estavel": "Uniao Estavel",
    }
    return valores.get(chave, _normalizar_texto(valor) or "Nao informado")


def _chave_texto(valor: str | None) -> str:
    texto = _normalizar_texto(valor)
    if texto is None:
        return ""
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ascii", "ignore")
        .decode("ascii")
        .casefold()
    )
