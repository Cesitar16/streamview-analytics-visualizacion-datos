"""Punto de extensión para la limpieza reproducible del catálogo.

No se implementan transformaciones hasta revisar la calidad y estructura de
los datasets RAW en el notebook de exploración.
"""

from typing import Any


def clean_catalog(*args: Any, **kwargs: Any) -> None:
    """Reservar la futura preparación documentada de los datos."""
    raise NotImplementedError("La limpieza se implementará tras la exploración.")
