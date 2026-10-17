"""Shared, testable selections and summaries for the EP2 dashboards."""

from pathlib import Path

import pandas as pd

from src.data_cleaning import build_catalog_views
from src.financial_rules import gross_roi_approx


ROOT = Path(__file__).resolve().parents[1]
MOVIES = ROOT / "data/raw/netflix_movies_detailed_up_to_2025.csv"
SHOWS = ROOT / "data/raw/netflix_tv_shows_detailed_up_to_2025.csv"


def load_views() -> dict[str, object]:
    missing = [str(path) for path in (MOVIES, SHOWS) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Faltan fuentes oficiales en data/raw: {missing}")
    return build_catalog_views(MOVIES, SHOWS)


def select_catalog(
    views: dict[str, object],
    *,
    types: list[str] | None = None,
    years: tuple[int, int] = (2010, 2025),
    genres: list[str] | None = None,
    countries: list[str] | None = None,
    languages: list[str] | None = None,
    rating_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """Filter entities once; multivalue fields use semi-joins to avoid row inflation."""
    catalog = views["catalogo_general"]
    mask = catalog["release_year"].between(*years)
    if types:
        mask &= catalog["type"].isin(types)
    if languages:
        mask &= catalog["language"].isin(languages)
    if rating_range:
        mask &= catalog["vote_average"].between(*rating_range)
    selected = catalog.loc[mask].copy()
    for choices, table, column in (
        (genres, "catalogo_generos", "genre"),
        (countries, "catalogo_paises", "country"),
    ):
        if choices:
            ids = views[table].loc[views[table][column].isin(choices), "content_id"]
            selected = selected.loc[selected["content_id"].isin(ids)]
    return selected


def category_counts(
    selected: pd.DataFrame, auxiliary: pd.DataFrame, value_column: str
) -> pd.DataFrame:
    rows = auxiliary.loc[
        auxiliary["content_id"].isin(selected["content_id"]),
        ["content_id", value_column],
    ]
    return (
        rows.groupby(value_column, as_index=False)
        .agg(titles=("content_id", "nunique"))
        .sort_values(["titles", value_column], ascending=[False, True])
        .reset_index(drop=True)
    )


def genre_performance(selected: pd.DataFrame, views: dict[str, object]) -> pd.DataFrame:
    popular = selected.loc[
        selected["content_id"].isin(views["catalogo_popularity"]["content_id"]),
        ["content_id", "popularity"],
    ]
    rated = selected.loc[
        selected["vote_count"].gt(0), ["content_id", "vote_average"]
    ]
    bridge = views["catalogo_generos"][["content_id", "genre"]]
    popularity = bridge.merge(
        popular, on="content_id", how="inner", validate="many_to_one"
    )
    ratings = bridge.merge(
        rated, on="content_id", how="inner", validate="many_to_one"
    )
    popularity = popularity.groupby("genre", as_index=False).agg(
        titles=("content_id", "nunique"),
        median_popularity=("popularity", "median"),
    )
    ratings = ratings.groupby("genre", as_index=False).agg(
        rated_titles=("content_id", "nunique"),
        mean_rating=("vote_average", "mean"),
    )
    return popularity.merge(ratings, on="genre", how="left").sort_values("titles", ascending=False)


def country_performance(
    selected: pd.DataFrame, views: dict[str, object], minimum_titles: int
) -> pd.DataFrame:
    rated = selected.loc[
        selected["vote_count"].gt(0),
        ["content_id", "vote_average", "popularity"],
    ]
    joined = views["catalogo_paises"][["content_id", "country"]].merge(
        rated, on="content_id", how="inner", validate="many_to_one"
    )
    summary = joined.groupby("country", as_index=False).agg(
        titles=("content_id", "nunique"),
        mean_rating=("vote_average", "mean"),
        median_popularity=("popularity", "median"),
    )
    return summary.loc[summary["titles"].ge(minimum_titles)].copy()


def financial_selection(selected: pd.DataFrame, views: dict[str, object]) -> pd.DataFrame:
    movie_ids = set(selected.loc[selected["type"].eq("Movie"), "show_id"])
    finance = views["movies_financial_valid"].loc[
        views["movies_financial_valid"]["show_id"].isin(movie_ids)
    ].copy()
    finance["return_multiple"] = finance["revenue"] / finance["budget"]
    return finance


def financial_summary(finance: pd.DataFrame) -> dict[str, float | int | None]:
    budget = float(finance["budget"].sum())
    revenue = float(finance["revenue"].sum())
    return {
        "eligible_movies": int(len(finance)),
        "total_budget": budget,
        "average_budget": float(finance["budget"].mean()) if len(finance) else 0.0,
        "total_revenue": revenue,
        "portfolio_multiple": revenue / budget if budget else 0.0,
        "gross_roi_approx": gross_roi_approx(finance),
        "median_title_multiple": float(finance["return_multiple"].median()) if len(finance) else 0.0,
    }
