"""Utilidades pequeñas para transformaciones reproducibles del catálogo."""

from collections.abc import Sequence
from pathlib import Path

import pandas as pd


def explode_multivalue_column(
    dataframe: pd.DataFrame,
    source_column: str,
    value_column: str,
    identifier_columns: Sequence[str] = ("content_id", "show_id", "type", "title"),
) -> tuple[pd.DataFrame, int]:
    """Deriva una tabla de valores individuales sin mutar el DataFrame de origen.

    Conserva solo filas con información en la columna origen, separa valores por
    coma, elimina espacios de borde y valores vacíos, y deduplica exclusivamente
    la combinación content_id más el valor individual. Actualmente se asume la coma
    (,) como separador de valores múltiples, decisión respaldada por la auditoría
    previa del catálogo.

    Returns:
        Una tabla nueva con identificadores y la cantidad de duplicados internos
        eliminados.
    """
    required_columns = [*identifier_columns, source_column]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise KeyError(f"Columnas requeridas no disponibles: {missing_columns}")

    auxiliary = dataframe.loc[
        dataframe[source_column].notna(), required_columns
    ].copy()
    auxiliary[value_column] = auxiliary[source_column].astype("string").str.split(",")
    if value_column != source_column:
        auxiliary = auxiliary.drop(columns=source_column)
    auxiliary = auxiliary.explode(value_column)
    auxiliary[value_column] = auxiliary[value_column].astype("string").str.strip()
    auxiliary = auxiliary.loc[
        auxiliary[value_column].notna() & auxiliary[value_column].ne("")
    ].copy()

    duplicate_mask = auxiliary.duplicated(subset=["content_id", value_column])
    duplicates_removed = int(duplicate_mask.sum())
    auxiliary = auxiliary.loc[~duplicate_mask].reset_index(drop=True)
    return auxiliary, duplicates_removed


def build_catalog_views(
    movies_path: str | Path,
    tv_shows_path: str | Path,
) -> dict[str, object]:
    """Reconstruye en memoria las vistas de catálogo aprobadas en Etapas 1 a 3.

    La función es determinista: recibe las dos fuentes RAW, conserva sus archivos
    sin modificaciones y aplica solo las reglas ya documentadas para identificación,
    fechas, espacios de borde, conflictos de popularity y campos multivalor.
    """
    text_columns = [
        "title",
        "director",
        "cast",
        "country",
        "genres",
        "language",
        "description",
    ]

    def prepare_source(path: str | Path) -> pd.DataFrame:
        prepared = pd.read_csv(path).copy(deep=True)
        prepared["show_id"] = prepared["show_id"].astype("string")
        prepared["date_added"] = pd.to_datetime(prepared["date_added"], errors="coerce")
        for column in text_columns:
            prepared[column] = prepared[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )
        return prepared

    def detect_popularity_conflicts(dataframe: pd.DataFrame) -> pd.Index:
        conflict_ids = []
        repeated = dataframe.loc[dataframe["show_id"].duplicated(keep=False)]
        for show_id, group in repeated.groupby("show_id", sort=True):
            comparable = group.astype(object).where(group.notna(), "<NA>")
            varying_columns = [
                column
                for column in group.columns
                if comparable[column].nunique(dropna=False) > 1
            ]
            if group["title"].nunique(dropna=False) == 1 and varying_columns == ["popularity"]:
                conflict_ids.append(show_id)
        return pd.Index(conflict_ids, dtype="string")

    movies_prepared = prepare_source(movies_path)
    tv_prepared = prepare_source(tv_shows_path)
    popularity_conflict_ids = detect_popularity_conflicts(tv_prepared)
    tv_prepared["popularity_conflict"] = tv_prepared["show_id"].isin(
        popularity_conflict_ids
    )

    tv_catalogo_general = tv_prepared.drop_duplicates(subset="show_id", keep="first").copy()
    tv_catalogo_general.loc[
        tv_catalogo_general["popularity_conflict"], "popularity"
    ] = float("nan")

    movies_catalogo_general = movies_prepared.copy()
    movies_catalogo_general["popularity_conflict"] = False
    movies_catalogo_general["financial_complete"] = (
        movies_catalogo_general["budget"].gt(0)
        & movies_catalogo_general["revenue"].gt(0)
    )
    common_columns = sorted(
        set(movies_catalogo_general.columns).intersection(tv_catalogo_general.columns)
    )
    catalogo_general = pd.concat(
        [
            movies_catalogo_general[common_columns],
            tv_catalogo_general[common_columns],
        ],
        ignore_index=True,
    )
    catalogo_general["content_id"] = (
        catalogo_general["type"].astype("string")
        + "_"
        + catalogo_general["show_id"].astype("string")
    )
    catalogo_popularity = catalogo_general.loc[
        ~catalogo_general["popularity_conflict"] & catalogo_general["popularity"].notna()
    ].copy()
    movies_financial_valid = movies_catalogo_general.loc[
        movies_catalogo_general["financial_complete"]
    ].copy()

    catalogo_generos, generos_duplicates_removed = explode_multivalue_column(
        catalogo_general, "genres", "genre"
    )
    catalogo_paises, paises_duplicates_removed = explode_multivalue_column(
        catalogo_general, "country", "country"
    )
    catalogo_directores, directores_duplicates_removed = explode_multivalue_column(
        catalogo_general, "director", "director"
    )
    catalogo_cast, cast_duplicates_removed = explode_multivalue_column(
        catalogo_general, "cast", "actor"
    )

    return {
        "movies_prepared": movies_prepared,
        "tv_prepared": tv_prepared,
        "catalogo_general": catalogo_general,
        "catalogo_popularity": catalogo_popularity,
        "movies_financial_valid": movies_financial_valid,
        "catalogo_generos": catalogo_generos,
        "catalogo_paises": catalogo_paises,
        "catalogo_directores": catalogo_directores,
        "catalogo_cast": catalogo_cast,
        "popularity_conflict_ids": popularity_conflict_ids,
        "auxiliary_duplicates_removed": {
            "catalogo_generos": generos_duplicates_removed,
            "catalogo_paises": paises_duplicates_removed,
            "catalogo_directores": directores_duplicates_removed,
            "catalogo_cast": cast_duplicates_removed,
        },
    }
