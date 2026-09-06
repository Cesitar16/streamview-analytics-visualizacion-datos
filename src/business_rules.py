"""Punto de extensión para reglas de negocio y variables derivadas.

Las reglas se implementarán después de validar los campos disponibles y su
calidad; las métricas financieras se limitarán a películas cuando corresponda.
"""

from typing import Any


def apply_business_rules(*args: Any, **kwargs: Any) -> None:
    """Reservar la futura aplicación de reglas del caso StreamView."""
    raise NotImplementedError("Las reglas se implementarán tras la exploración.")
