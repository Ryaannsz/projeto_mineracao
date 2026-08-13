from __future__ import annotations

import unicodedata
from collections.abc import Iterable

from models import (
    DadosFonte,
    DimensaoCliente,
    DimensaoData,
    DimensaoProduto,
    DimensaoServico,
    FatoAtendimentoServico,
    FatoItemVenda,
    LoteOlap,
    chave_origem,
)


class ServicoTransformacao:
    """Padroniza as fontes e produz registros no grao do futuro modelo OLAP."""

    def transformar(self, fontes: Iterable[DadosFonte]) -> LoteOlap:
        fontes = tuple(fontes)
        clientes = self._transformar_clientes(fontes)
        produtos = self._transformar_produtos(fontes)
        servicos = self._transformar_servicos(fontes)
        fatos_itens_venda = self._transformar_itens_venda(fontes, clientes, produtos)
        fatos_atendimentos = self._transformar_atendimentos(fontes, clientes, servicos)
        datas = self._transformar_datas(fatos_itens_venda, fatos_atendimentos)

        return LoteOlap(
            clientes=tuple(clientes.values()),
            datas=datas,
            produtos=tuple(produtos.values()),
            servicos=tuple(servicos.values()),
            fatos_itens_venda=tuple(fatos_itens_venda),
            fatos_atendimentos_servico=tuple(fatos_atendimentos),
        )

    @staticmethod
    def _transformar_clientes(fontes: tuple[DadosFonte, ...]) -> dict[str, DimensaoCliente]:
        clientes: dict[str, DimensaoCliente] = {}
        for dados in fontes:
            for cliente in dados.clientes:
                chave = chave_origem(dados.origem, cliente.id_cliente)
                clientes[chave] = DimensaoCliente(
                    chave_natural=chave,
                    origem=dados.origem,
                    codigo_origem=cliente.id_cliente,
                    nome=_texto_obrigatorio(cliente.nome),
                    email=_normalizar_email(cliente.email),
                    telefone=_normalizar_texto(cliente.telefone),
                    sexo=_normalizar_sexo(cliente.sexo),
                    estado_civil=_normalizar_estado_civil(cliente.estado_civil),
                    data_nascimento=cliente.data_nascimento,
                    data_cadastro=cliente.data_cadastro,
                )
        return clientes

    @staticmethod
    def _transformar_produtos(fontes: tuple[DadosFonte, ...]) -> dict[str, DimensaoProduto]:
        produtos: dict[str, DimensaoProduto] = {}
        for dados in fontes:
            for produto in dados.produtos:
                chave = chave_origem(dados.origem, produto.id_produto)
                produtos[chave] = DimensaoProduto(
                    chave_natural=chave,
                    origem=dados.origem,
                    codigo_origem=produto.id_produto,
                    nome=_texto_obrigatorio(produto.nome),
                    categoria=_normalizar_texto(produto.categoria),
                    preco=produto.preco,
                )
        return produtos

    @staticmethod
    def _transformar_servicos(fontes: tuple[DadosFonte, ...]) -> dict[str, DimensaoServico]:
        servicos: dict[str, DimensaoServico] = {}
        for dados in fontes:
            for servico in dados.servicos:
                chave = chave_origem(dados.origem, servico.id_servico)
                servicos[chave] = DimensaoServico(
                    chave_natural=chave,
                    origem=dados.origem,
                    codigo_origem=servico.id_servico,
                    descricao=_texto_obrigatorio(servico.descricao),
                    valor=servico.valor,
                )
        return servicos

    @staticmethod
    def _transformar_itens_venda(
        fontes: tuple[DadosFonte, ...],
        clientes: dict[str, DimensaoCliente],
        produtos: dict[str, DimensaoProduto],
    ) -> list[FatoItemVenda]:
        vendas = {
            chave_origem(dados.origem, venda.id_venda): venda
            for dados in fontes
            for venda in dados.vendas
        }
        fatos: list[FatoItemVenda] = []
        for dados in fontes:
            for item in dados.itens_venda:
                chave_venda = chave_origem(dados.origem, item.id_venda)
                venda = vendas.get(chave_venda)
                if venda is None:
                    raise ValueError(f"Item {item.id_item} sem venda correspondente.")

                chave_cliente = chave_origem(dados.origem, venda.id_cliente)
                chave_produto = chave_origem(dados.origem, item.id_produto)
                _validar_referencia(chave_cliente, clientes, "cliente")
                _validar_referencia(chave_produto, produtos, "produto")

                fatos.append(
                    FatoItemVenda(
                        chave_natural=chave_origem(dados.origem, item.id_item),
                        origem=dados.origem,
                        codigo_venda_origem=venda.id_venda,
                        chave_cliente_natural=chave_cliente,
                        chave_produto_natural=chave_produto,
                        chave_data=_chave_data(venda.data_venda),
                        data_venda=venda.data_venda,
                        quantidade=item.quantidade,
                        valor_unitario=item.valor_unitario,
                        valor_total_item=item.quantidade * item.valor_unitario,
                    )
                )
        return fatos

    @staticmethod
    def _transformar_atendimentos(
        fontes: tuple[DadosFonte, ...],
        clientes: dict[str, DimensaoCliente],
        servicos: dict[str, DimensaoServico],
    ) -> list[FatoAtendimentoServico]:
        fatos: list[FatoAtendimentoServico] = []
        for dados in fontes:
            for atendimento in dados.atendimentos_servico:
                chave_cliente = chave_origem(dados.origem, atendimento.id_cliente)
                chave_servico = chave_origem(dados.origem, atendimento.id_servico)
                _validar_referencia(chave_cliente, clientes, "cliente")
                _validar_referencia(chave_servico, servicos, "servico")
                fatos.append(
                    FatoAtendimentoServico(
                        chave_natural=chave_origem(dados.origem, atendimento.id_atendimento),
                        origem=dados.origem,
                        chave_cliente_natural=chave_cliente,
                        chave_servico_natural=chave_servico,
                        chave_data=_chave_data(atendimento.data_atendimento),
                        data_atendimento=atendimento.data_atendimento,
                        valor_cobrado=atendimento.valor_cobrado,
                    )
                )
        return fatos

    @staticmethod
    def _transformar_datas(
        fatos_itens_venda: list[FatoItemVenda],
        fatos_atendimentos: list[FatoAtendimentoServico],
    ) -> tuple[DimensaoData, ...]:
        datas = sorted(
            {fato.data_venda for fato in fatos_itens_venda}
            | {fato.data_atendimento for fato in fatos_atendimentos}
        )
        return tuple(
            DimensaoData(
                chave_data=_chave_data(data),
                data=data,
                ano=data.year,
                trimestre=(data.month - 1) // 3 + 1,
                mes=data.month,
                dia=data.day,
            )
            for data in datas
        )


def _validar_referencia(chave: str, registros: dict, tipo: str) -> None:
    if chave not in registros:
        raise ValueError(f"Referencia de {tipo} inexistente: {chave}.")


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


def _normalizar_email(valor: str | None) -> str | None:
    texto = _normalizar_texto(valor)
    return texto.lower() if texto else None


def _normalizar_sexo(valor: str | None) -> str | None:
    chave = _chave_texto(valor)
    if chave in {"m", "masculino"}:
        return "M"
    if chave in {"f", "feminino"}:
        return "F"
    return None


def _normalizar_estado_civil(valor: str | None) -> str | None:
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
    return valores.get(chave, _normalizar_texto(valor))


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


def _chave_data(data: date) -> int:
    return data.year * 10_000 + data.month * 100 + data.day
