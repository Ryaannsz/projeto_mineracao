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
        tempos: dict[str, DimensaoTempo] = {}
        produtos: dict[str, DimensaoProduto] = {}
        cidades: dict[str, DimensaoCidade] = {}
        estados_civis: dict[str, DimensaoEstadoCivil] = {}
        agregados: dict[tuple[str, str, str, str], list] = defaultdict(
            lambda: [0, Decimal("0")]
        )

        for venda in silver.vendas:
            chave_tempo = f"{venda.ano}Q{venda.quadrimestre}"
            chave_produto = _chave_produto(venda.produto, venda.categoria)
            chave_cidade = _chave_texto(venda.cidade)
            chave_estado_civil = _chave_texto(venda.estado_civil)

            tempos[chave_tempo] = DimensaoTempo(chave_tempo, venda.ano, venda.quadrimestre)
            produtos[chave_produto] = DimensaoProduto(chave_produto, venda.produto, venda.categoria)
            cidades[chave_cidade] = DimensaoCidade(chave_cidade, venda.cidade)
            estados_civis[chave_estado_civil] = DimensaoEstadoCivil(
                chave_estado_civil, venda.estado_civil
            )
            agregado = agregados[(chave_tempo, chave_produto, chave_cidade, chave_estado_civil)]
            agregado[0] += venda.quantidade
            agregado[1] += venda.valor_vendido

        fatos = tuple(
            FatoVenda(
                chave_tempo_natural=chaves[0],
                chave_produto_natural=chaves[1],
                chave_cidade_natural=chaves[2],
                chave_estado_civil_natural=chaves[3],
                quantidade_vendida=valores[0],
                valor_vendido=valores[1],
            )
            for chaves, valores in sorted(agregados.items())
        )
        return LoteOlap(
            tempos=tuple(sorted(tempos.values(), key=lambda item: item.chave_natural)),
            produtos=tuple(sorted(produtos.values(), key=lambda item: item.chave_natural)),
            cidades=tuple(sorted(cidades.values(), key=lambda item: item.chave_natural)),
            estados_civis=tuple(
                sorted(estados_civis.values(), key=lambda item: item.chave_natural)
            ),
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


def _chave_produto(nome: str, categoria: str) -> str:
    return f"{_chave_texto(nome)}|{_chave_texto(categoria)}"


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
