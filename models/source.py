from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class FonteDados(str, Enum):
    SALVADOR = "salvador"
    ITABUNA = "itabuna"
    FEIRA_DE_SANTANA = "feira_de_santana"


def chave_origem(origem: FonteDados, identificador: str) -> str:
    """Cria uma chave natural unica entre as tres fontes."""
    return f"{origem.value}:{identificador}"


@dataclass(frozen=True, slots=True)
class ClienteOrigem:
    origem: FonteDados
    id_cliente: str
    nome: str
    email: str | None
    telefone: str | None
    sexo: str | None
    estado_civil: str | None
    data_nascimento: date | None
    data_cadastro: date | None


@dataclass(frozen=True, slots=True)
class ProdutoOrigem:
    origem: FonteDados
    id_produto: str
    nome: str
    categoria: str | None
    preco: Decimal


@dataclass(frozen=True, slots=True)
class VendaOrigem:
    origem: FonteDados
    id_venda: str
    id_cliente: str
    data_venda: date
    valor_total: Decimal | None


@dataclass(frozen=True, slots=True)
class ItemVendaOrigem:
    origem: FonteDados
    id_item: str
    id_venda: str
    id_produto: str
    quantidade: int
    valor_unitario: Decimal


@dataclass(frozen=True, slots=True)
class ServicoOrigem:
    origem: FonteDados
    id_servico: str
    descricao: str
    valor: Decimal


@dataclass(frozen=True, slots=True)
class AtendimentoServicoOrigem:
    origem: FonteDados
    id_atendimento: str
    id_cliente: str
    id_servico: str
    data_atendimento: date
    valor_cobrado: Decimal


@dataclass(frozen=True, slots=True)
class DadosFonte:
    origem: FonteDados
    clientes: tuple[ClienteOrigem, ...] = ()
    produtos: tuple[ProdutoOrigem, ...] = ()
    vendas: tuple[VendaOrigem, ...] = ()
    itens_venda: tuple[ItemVendaOrigem, ...] = ()
    servicos: tuple[ServicoOrigem, ...] = ()
    atendimentos_servico: tuple[AtendimentoServicoOrigem, ...] = ()
