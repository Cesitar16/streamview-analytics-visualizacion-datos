"""Reglas y KPIs del bloque analítico de Lucas Moncada.

Las funciones reciben exclusivamente las vistas preparadas por ``data_cleaning``.
No leen, limpian ni modifican los CSV RAW.
"""

from collections.abc import Mapping

import pandas as pd


ANALYSIS_START_YEAR = 2010
ANALYSIS_END_YEAR = 2025
REQUIRED_COLUMNS = {
    "content_id",
    "title",
    "type",
    "release_year",
    "date_added",
    "popularity",
    "vote_average",
    "vote_count",
}


def _validate_view(dataframe: pd.DataFrame, view_name: str) -> None:
    missing = sorted(REQUIRED_COLUMNS.difference(dataframe.columns))
    if missing:
        raise KeyError(f"{view_name} no contiene las columnas requeridas: {missing}")


def _rated_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Retorna títulos con evidencia de valoración sin reinterpretar el dato original."""
    return dataframe.loc[
        dataframe["vote_count"].gt(0) & dataframe["vote_average"].notna()
    ].copy()


def popularity_comparison(catalogo_popularity: pd.DataFrame) -> pd.DataFrame:
    """Resume la distribución de popularity por tipo sobre su vista aprobada."""
    _validate_view(catalogo_popularity, "catalogo_popularity")
    return (
        catalogo_popularity.groupby("type", as_index=False)
        .agg(
            titles=("content_id", "nunique"),
            mean_popularity=("popularity", "mean"),
            median_popularity=("popularity", "median"),
            q1_popularity=("popularity", lambda values: values.quantile(0.25)),
            q3_popularity=("popularity", lambda values: values.quantile(0.75)),
            max_popularity=("popularity", "max"),
        )
        .sort_values("type")
        .reset_index(drop=True)
    )


def rating_summary(catalogo_general: pd.DataFrame) -> pd.DataFrame:
    """Separa cobertura, puntaje y cantidad de votos por tipo de contenido."""
    _validate_view(catalogo_general, "catalogo_general")
    rated = _rated_rows(catalogo_general)
    totals = catalogo_general.groupby("type")["content_id"].nunique().rename("titles")
    rows: list[dict[str, object]] = []
    for content_type, group in rated.groupby("type", sort=True):
        total_votes = int(group["vote_count"].sum())
        rows.append(
            {
                "type": content_type,
                "titles": int(totals.loc[content_type]),
                "rated_titles": int(group["content_id"].nunique()),
                "mean_vote_average": float(group["vote_average"].mean()),
                "median_vote_average": float(group["vote_average"].median()),
                "weighted_vote_average": float(
                    (group["vote_average"] * group["vote_count"]).sum() / total_votes
                ),
                "median_vote_count": float(group["vote_count"].median()),
                "total_votes": total_votes,
            }
        )
    summary = pd.DataFrame(rows)
    summary["rating_coverage_pct"] = summary["rated_titles"] / summary["titles"] * 100
    return summary[
        [
            "type",
            "titles",
            "rated_titles",
            "rating_coverage_pct",
            "mean_vote_average",
            "median_vote_average",
            "weighted_vote_average",
            "median_vote_count",
            "total_votes",
        ]
    ]


def _spearman_without_scipy(x: pd.Series, y: pd.Series) -> float:
    """Calcula Spearman como Pearson sobre rangos promedio."""
    if len(x) < 2 or x.nunique() < 2 or y.nunique() < 2:
        return float("nan")
    return float(x.rank(method="average").corr(y.rank(method="average")))


def popularity_rating_association(catalogo_popularity: pd.DataFrame) -> pd.DataFrame:
    """Mide asociación monotónica usando solo títulos con uno o más votos."""
    _validate_view(catalogo_popularity, "catalogo_popularity")
    eligible = _rated_rows(catalogo_popularity).dropna(
        subset=["popularity", "vote_average"]
    )
    groups: list[tuple[str, pd.DataFrame]] = [("Overall", eligible)]
    groups.extend((str(name), group) for name, group in eligible.groupby("type", sort=True))
    return pd.DataFrame(
        [
            {
                "scope": scope,
                "titles": int(group["content_id"].nunique()),
                "spearman_rho": _spearman_without_scipy(
                    group["popularity"], group["vote_average"]
                ),
            }
            for scope, group in groups
        ]
    )


def content_rankings(
    catalogo_general: pd.DataFrame,
    catalogo_popularity: pd.DataFrame,
    top_n: int = 10,
) -> dict[str, pd.DataFrame]:
    """Construye los rankings explícitos de popularidad, valoración y votos."""
    _validate_view(catalogo_general, "catalogo_general")
    _validate_view(catalogo_popularity, "catalogo_popularity")
    if top_n < 1:
        raise ValueError("top_n debe ser mayor que cero")

    base_columns = [
        "content_id",
        "title",
        "type",
        "popularity",
        "vote_average",
        "vote_count",
    ]
    top_popularity = catalogo_popularity.sort_values(
        ["popularity", "vote_count", "title"],
        ascending=[False, False, True],
    ).head(top_n)[base_columns].copy()
    top_rated = _rated_rows(catalogo_general).sort_values(
        ["vote_average", "vote_count", "title"],
        ascending=[False, False, True],
    ).head(top_n)[base_columns].copy()
    top_voted = catalogo_general.sort_values(
        ["vote_count", "vote_average", "title"],
        ascending=[False, False, True],
    ).head(top_n)[base_columns].copy()

    for ranking in (top_popularity, top_rated, top_voted):
        ranking.insert(0, "rank", range(1, len(ranking) + 1))
        ranking.reset_index(drop=True, inplace=True)
    return {
        "top_popularity": top_popularity,
        "top_rated": top_rated,
        "top_voted": top_voted,
    }


def popularity_by_genre(
    catalogo_popularity: pd.DataFrame,
    catalogo_generos: pd.DataFrame,
) -> pd.DataFrame:
    """Resume popularity por género mediante content_id y vistas preparadas."""
    _validate_view(catalogo_popularity, "catalogo_popularity")
    missing = sorted({"content_id", "genre"}.difference(catalogo_generos.columns))
    if missing:
        raise KeyError(f"catalogo_generos no contiene las columnas requeridas: {missing}")

    joined = catalogo_generos[["content_id", "genre"]].merge(
        catalogo_popularity[["content_id", "popularity"]],
        on="content_id",
        how="inner",
        validate="many_to_one",
    )
    return (
        joined.groupby("genre", as_index=False)
        .agg(
            titles=("content_id", "nunique"),
            mean_popularity=("popularity", "mean"),
            median_popularity=("popularity", "median"),
        )
        .sort_values(["median_popularity", "titles"], ascending=[False, False])
        .reset_index(drop=True)
    )


def catalog_timeline(
    catalogo_general: pd.DataFrame,
    start_year: int = ANALYSIS_START_YEAR,
    end_year: int = ANALYSIS_END_YEAR,
) -> pd.DataFrame:
    """Distingue estrenos e incorporaciones anuales al catálogo."""
    _validate_view(catalogo_general, "catalogo_general")
    if start_year > end_year:
        raise ValueError("start_year no puede ser mayor que end_year")
    if not pd.api.types.is_datetime64_any_dtype(catalogo_general["date_added"]):
        raise TypeError("catalogo_general.date_added debe estar preparado como datetime")

    years = range(start_year, end_year + 1)
    releases = (
        catalogo_general.loc[catalogo_general["release_year"].isin(years)]
        .groupby(["release_year", "type"], as_index=False)
        .agg(titles=("content_id", "nunique"))
        .rename(columns={"release_year": "year"})
    )
    releases["event"] = "Estrenos"

    additions_source = catalogo_general.assign(
        date_added_year=catalogo_general["date_added"].dt.year
    )
    additions = (
        additions_source.loc[additions_source["date_added_year"].isin(years)]
        .groupby(["date_added_year", "type"], as_index=False)
        .agg(titles=("content_id", "nunique"))
        .rename(columns={"date_added_year": "year"})
    )
    additions["event"] = "Incorporaciones"
    return (
        pd.concat([releases, additions], ignore_index=True)
        [["year", "type", "event", "titles"]]
        .sort_values(["year", "type", "event"])
        .reset_index(drop=True)
    )


def temporal_alignment_summary(catalogo_general: pd.DataFrame) -> pd.DataFrame:
    """Cuantifica si año de estreno e incorporación pueden analizarse por separado."""
    _validate_view(catalogo_general, "catalogo_general")
    if not pd.api.types.is_datetime64_any_dtype(catalogo_general["date_added"]):
        raise TypeError("catalogo_general.date_added debe estar preparado como datetime")
    prepared = catalogo_general.assign(
        date_added_year=catalogo_general["date_added"].dt.year,
        year_gap=catalogo_general["date_added"].dt.year
        - catalogo_general["release_year"],
    )
    rows = []
    for content_type, group in prepared.groupby("type", sort=True):
        same_year = group["date_added_year"].eq(group["release_year"])
        rows.append(
            {
                "type": content_type,
                "titles": int(group["content_id"].nunique()),
                "same_year_titles": int(same_year.sum()),
                "same_year_pct": float(same_year.mean() * 100),
                "median_year_gap": float(group["year_gap"].median()),
                "min_year_gap": int(group["year_gap"].min()),
                "max_year_gap": int(group["year_gap"].max()),
            }
        )
    return pd.DataFrame(rows)


def historical_evolution(
    catalogo_general: pd.DataFrame,
    catalogo_popularity: pd.DataFrame,
    start_year: int = ANALYSIS_START_YEAR,
    end_year: int = ANALYSIS_END_YEAR,
) -> pd.DataFrame:
    """Construye una serie 2010–2025 por año de estreno y tipo de contenido."""
    _validate_view(catalogo_general, "catalogo_general")
    _validate_view(catalogo_popularity, "catalogo_popularity")
    if start_year > end_year:
        raise ValueError("start_year no puede ser mayor que end_year")

    years = range(start_year, end_year + 1)
    general = catalogo_general.loc[catalogo_general["release_year"].isin(years)].copy()
    popularity = catalogo_popularity.loc[
        catalogo_popularity["release_year"].isin(years)
    ].copy()
    rated = _rated_rows(general)
    counts = general.groupby(["release_year", "type"], as_index=False).agg(
        titles=("content_id", "nunique")
    )
    popularity_year = popularity.groupby(
        ["release_year", "type"], as_index=False
    ).agg(
        popularity_titles=("content_id", "nunique"),
        median_popularity=("popularity", "median"),
    )
    rating_year = rated.groupby(["release_year", "type"], as_index=False).agg(
        rated_titles=("content_id", "nunique"),
        median_vote_average=("vote_average", "median"),
        median_vote_count=("vote_count", "median"),
    )
    evolution = counts.merge(
        popularity_year, on=["release_year", "type"], how="left"
    ).merge(rating_year, on=["release_year", "type"], how="left")
    evolution["popularity_titles"] = evolution["popularity_titles"].fillna(0).astype(int)
    evolution["rated_titles"] = evolution["rated_titles"].fillna(0).astype(int)
    evolution["rating_coverage_pct"] = evolution["rated_titles"] / evolution["titles"] * 100
    return evolution.sort_values(["release_year", "type"]).reset_index(drop=True)


def kpi_summary(analysis_tables: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Presenta los indicadores principales con unidad y definición auditable."""
    popularity = analysis_tables["popularity_comparison"]
    rating = analysis_tables["rating_summary"]
    association = analysis_tables["popularity_rating_association"]
    history = analysis_tables["historical_evolution"]
    rows: list[dict[str, object]] = []
    for row in popularity.itertuples(index=False):
        rows.extend(
            [
                {
                    "kpi": "Popularidad promedio",
                    "scope": row.type,
                    "value": row.mean_popularity,
                    "unit": "índice de popularidad",
                    "definition": "Media en catalogo_popularity; conflictos excluidos.",
                },
                {
                    "kpi": "Popularidad mediana",
                    "scope": row.type,
                    "value": row.median_popularity,
                    "unit": "índice de popularidad",
                    "definition": "Mediana en catalogo_popularity; conflictos excluidos.",
                },
            ]
        )
    for row in rating.itertuples(index=False):
        rows.extend(
            [
                {
                    "kpi": "Cobertura de valoración",
                    "scope": row.type,
                    "value": row.rating_coverage_pct,
                    "unit": "% de títulos",
                    "definition": "Títulos con vote_count > 0 sobre catalogo_general.",
                },
                {
                    "kpi": "Calificación promedio",
                    "scope": row.type,
                    "value": row.mean_vote_average,
                    "unit": "puntos (0–10)",
                    "definition": "Media de vote_average entre títulos con votos.",
                },
                {
                    "kpi": "Valoración mediana",
                    "scope": row.type,
                    "value": row.median_vote_average,
                    "unit": "puntos (0–10)",
                    "definition": "Mediana de vote_average entre títulos con votos.",
                },
                {
                    "kpi": "Votos medianos",
                    "scope": row.type,
                    "value": row.median_vote_count,
                    "unit": "votos",
                    "definition": "Mediana de vote_count entre títulos con votos.",
                },
            ]
        )
    for row in association.itertuples(index=False):
        rows.append(
            {
                "kpi": "Asociación popularidad–valoración",
                "scope": row.scope,
                "value": row.spearman_rho,
                "unit": "rho de Spearman",
                "definition": "Asociación monotónica con vote_count > 0.",
            }
        )
    for content_type, group in history.groupby("type", sort=True):
        peak = group.loc[group["median_popularity"].idxmax()]
        rows.append(
            {
                "kpi": "Año de mayor popularidad mediana",
                "scope": content_type,
                "value": int(peak["release_year"]),
                "unit": "año de estreno",
                "definition": "Máximo anual de la mediana entre 2010 y 2025.",
            }
        )
    return pd.DataFrame(rows)


def build_lucas_analysis(
    catalogo_general: pd.DataFrame,
    catalogo_popularity: pd.DataFrame,
    catalogo_generos: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Calcula todas las tablas reproducibles de los objetivos de Lucas Moncada."""
    tables = {
        "popularity_comparison": popularity_comparison(catalogo_popularity),
        "rating_summary": rating_summary(catalogo_general),
        "popularity_rating_association": popularity_rating_association(catalogo_popularity),
        "historical_evolution": historical_evolution(catalogo_general, catalogo_popularity),
        "popularity_by_genre": popularity_by_genre(
            catalogo_popularity, catalogo_generos
        ),
        "catalog_timeline": catalog_timeline(catalogo_general),
        "temporal_alignment": temporal_alignment_summary(catalogo_general),
    }
    tables.update(content_rankings(catalogo_general, catalogo_popularity))
    tables["kpi_summary"] = kpi_summary(tables)
    return tables
