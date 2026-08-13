from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def para_data(valor: Any) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        return date.fromisoformat(valor)
    raise TypeError(f"Nao foi possivel converter {valor!r} para data.")


def para_decimal(valor: Any) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    return Decimal(str(valor))
