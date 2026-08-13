from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .source import FonteDados


@dataclass(frozen=True, slots=True)
class DimensaoCliente:
    chave_natural: str
    origem: FonteDados
    codigo_origem: str
    nome: str
    email: str | None
    telefone: str | None
    sexo: str | None
    estado_civil: str | None
    data_nascimento: date | None
    data_cadastro: date | None


@dataclass(frozen=True, slots=True)
class DimensaoData:
    chave_data: int
    data: date
    ano: int
    trimestre: int
    mes: int
    dia: int


@dataclass(frozen=True, slots=True)
class DimensaoProduto:
    chave_natural: str
    origem: FonteDados
    codigo_origem: str
    nome: str
    categoria: str | None
    preco: Decimal


@dataclass(frozen=True, slots=True)
class DimensaoServico:
    chave_natural: str
    origem: FonteDados
    codigo_origem: str
    descricao: str
    valor: Decimal


@dataclass(frozen=True, slots=True)
class FatoItemVenda:
    chave_natural: str
    origem: FonteDados
    codigo_venda_origem: str
    chave_cliente_natural: str
    chave_produto_natural: str
    chave_data: int
    data_venda: date
    quantidade: int
    valor_unitario: Decimal
    valor_total_item: Decimal


@dataclass(frozen=True, slots=True)
class FatoAtendimentoServico:
    chave_natural: str
    origem: FonteDados
    chave_cliente_natural: str
    chave_servico_natural: str
    chave_data: int
    data_atendimento: date
    valor_cobrado: Decimal


@dataclass(frozen=True, slots=True)
class LoteOlap:
    clientes: tuple[DimensaoCliente, ...]
    datas: tuple[DimensaoData, ...]
    produtos: tuple[DimensaoProduto, ...]
    servicos: tuple[DimensaoServico, ...]
    fatos_itens_venda: tuple[FatoItemVenda, ...]
    fatos_atendimentos_servico: tuple[FatoAtendimentoServico, ...]

    def quantidades(self) -> dict[str, int]:
        return {
            "dimensao_clientes": len(self.clientes),
            "dimensao_datas": len(self.datas),
            "dimensao_produtos": len(self.produtos),
            "dimensao_servicos": len(self.servicos),
            "fato_itens_venda": len(self.fatos_itens_venda),
            "fato_atendimentos_servico": len(self.fatos_atendimentos_servico),
        }
