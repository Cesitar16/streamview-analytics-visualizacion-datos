"""Reglas reproducibles para el análisis financiero de Ignacio Silva.

Las funciones reciben exclusivamente ``movies_financial_valid`` creada por
``build_catalog_views``. No leen ni transforman los CSV RAW.
"""

from collections.abc import Mapping

import pandas as pd


REQUIRED_COLUMNS = {"show_id", "title", "budget", "revenue"}


def validate_financial_view(movies_financial_valid: pd.DataFrame) -> None:
    """Comprueba el contrato de la vista financiera sin modificarla."""
    missing = sorted(REQUIRED_COLUMNS.difference(movies_financial_valid.columns))
    if missing:
        raise KeyError(
            "movies_financial_valid no contiene las columnas requeridas: "
            f"{missing}"
        )
    if movies_financial_valid["show_id"].isna().any() or not movies_financial_valid["show_id"].is_unique:
        raise ValueError("movies_financial_valid debe tener show_id únicos y no nulos")
    if not movies_financial_valid["budget"].gt(0).all():
        raise ValueError("movies_financial_valid requiere budget > 0")
    if not movies_financial_valid["revenue"].gt(0).all():
        raise ValueError("movies_financial_valid requiere revenue > 0")


def add_roi_approx(movies_financial_valid: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia con ROI aproximado definido por el caso: revenue / budget."""
    validate_financial_view(movies_financial_valid)
    financial = movies_financial_valid.copy(deep=True)
    financial["roi_approx"] = financial["revenue"] / financial["budget"]
    return financial


def _spearman(x: pd.Series, y: pd.Series) -> float:
    """Calcula Spearman como la correlación de rangos, sin nueva dependencia."""
    if len(x) < 2 or x.nunique() < 2 or y.nunique() < 2:
        return float("nan")
    return float(x.rank(method="average").corr(y.rank(method="average")))


def financial_association(financial: pd.DataFrame) -> pd.DataFrame:
    """Resume la asociación monotónica entre presupuesto e ingresos."""
    required = {"budget", "revenue"}
    missing = sorted(required.difference(financial.columns))
    if missing:
        raise KeyError(f"financial no contiene las columnas requeridas: {missing}")
    return pd.DataFrame(
        [{"titles": int(len(financial)), "spearman_rho": _spearman(financial["budget"], financial["revenue"])}]
    )


def financial_kpis(financial: pd.DataFrame, total_movies: int) -> pd.DataFrame:
    """Construye KPIs financieros con unidad y definición auditables."""
    if total_movies < len(financial):
        raise ValueError("total_movies no puede ser menor que las películas elegibles")
    values = [
        ("Cobertura financiera", len(financial) / total_movies * 100, "% de Movies", "Películas elegibles sobre Movies totales."),
        ("Películas elegibles", len(financial), "películas", "Filas con budget > 0 y revenue > 0."),
        ("Presupuesto total", financial["budget"].sum(), "USD", "Suma de budget en la vista financiera."),
        ("Presupuesto promedio", financial["budget"].mean(), "USD", "Media de budget en la vista financiera."),
        ("Presupuesto mediano", financial["budget"].median(), "USD", "Mediana de budget ante asimetría."),
        ("Ingresos totales", financial["revenue"].sum(), "USD", "Suma de revenue en la vista financiera."),
        ("Ingresos promedio", financial["revenue"].mean(), "USD", "Media de revenue en la vista financiera."),
        ("Ingresos medianos", financial["revenue"].median(), "USD", "Mediana de revenue ante asimetría."),
        ("ROI aproximado promedio", financial["roi_approx"].mean(), "multiplicador", "Media de revenue / budget por película."),
        ("ROI aproximado mediano", financial["roi_approx"].median(), "multiplicador", "Mediana de revenue / budget por película."),
    ]
    return pd.DataFrame(values, columns=["kpi", "value", "unit", "definition"])


def financial_rankings(financial: pd.DataFrame, top_n: int = 10) -> dict[str, pd.DataFrame]:
    """Entrega rankings estables de ingreso absoluto y retorno relativo."""
    if top_n < 1:
        raise ValueError("top_n debe ser mayor que cero")
    columns = ["show_id", "title", "budget", "revenue", "roi_approx"]
    top_revenue = financial.sort_values(
        ["revenue", "budget", "title", "show_id"], ascending=[False, False, True, True]
    ).head(top_n)[columns].copy()
    top_roi = financial.sort_values(
        ["roi_approx", "revenue", "budget", "title", "show_id"],
        ascending=[False, False, True, True, True],
    ).head(top_n)[columns].copy()
    for table in (top_revenue, top_roi):
        table.insert(0, "rank", range(1, len(table) + 1))
        table.reset_index(drop=True, inplace=True)
    return {"top_revenue": top_revenue, "top_roi": top_roi}


def low_budget_high_return(financial: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Segmenta presupuesto <= P25 y ROI aproximado >= P75 de forma reproducible."""
    budget_p25 = float(financial["budget"].quantile(0.25))
    roi_p75 = float(financial["roi_approx"].quantile(0.75))
    segment = financial.loc[
        financial["budget"].le(budget_p25) & financial["roi_approx"].ge(roi_p75)
    ].copy()
    segment = segment.sort_values(
        ["roi_approx", "revenue", "title", "show_id"], ascending=[False, False, True, True]
    ).reset_index(drop=True)
    thresholds = pd.DataFrame(
        [{"budget_p25": budget_p25, "roi_approx_p75": roi_p75, "titles": int(len(segment))}]
    )
    return segment, thresholds


def build_financial_analysis(
    movies_financial_valid: pd.DataFrame, total_movies: int = 16_000
) -> Mapping[str, pd.DataFrame]:
    """Calcula todas las tablas del bloque financiero sin mutar su entrada."""
    financial = add_roi_approx(movies_financial_valid)
    segment, thresholds = low_budget_high_return(financial)
    tables: dict[str, pd.DataFrame] = {
        "financial_movies": financial,
        "financial_association": financial_association(financial),
        "financial_kpis": financial_kpis(financial, total_movies),
        "low_budget_high_return": segment,
        "low_budget_thresholds": thresholds,
    }
    tables.update(financial_rankings(financial))
    return tables
