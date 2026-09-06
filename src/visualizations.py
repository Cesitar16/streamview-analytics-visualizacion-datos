"""Punto de extensión para visualizaciones y recursos narrativos.

No se definen gráficos ni indicadores antes de completar la preparación de los
datos y las reglas de negocio.
"""

from typing import Any


def build_visualization(*args: Any, **kwargs: Any) -> None:
    """Reservar la futura construcción de visualizaciones."""
    raise NotImplementedError(
        "Las visualizaciones se implementarán tras preparar los datos."
    )
