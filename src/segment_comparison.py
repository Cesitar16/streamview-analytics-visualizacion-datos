"""Reusable metrics for comparing two catalogue segments without row inflation."""

import pandas as pd


DIMENSIONS = {
    "genre": ("catalogo_generos", "genre"),
    "country": ("catalogo_paises", "country"),
}


def annual_content_trend(selected: pd.DataFrame) -> pd.DataFrame:
    """Return unique-title counts per recorded year and content type.

    The source year is a recorded release year, not verified platform-ingestion
    history. Empty type/year combinations are retained as zero for line charts.
    """
    columns = ["release_year", "type", "titles"]
    if selected.empty:
        return pd.DataFrame(columns=columns)

    years = sorted(selected["release_year"].dropna().unique())
    types = [kind for kind in ("Movie", "TV Show") if kind in set(selected["type"])]
    counts = selected.groupby(["release_year", "type"], as_index=False).agg(
        titles=("content_id", "nunique")
    )
    index = pd.MultiIndex.from_product(
        [years, types], names=["release_year", "type"]
    )
    return (
        counts.set_index(["release_year", "type"])
        .reindex(index, fill_value=0)
        .reset_index()
        .loc[:, columns]
    )


def segment_selection(
    selected: pd.DataFrame,
    views: dict[str, object],
    *,
    dimension: str,
    category: str,
) -> pd.DataFrame:
    """Select one multivalue category using a semi-join on unique content IDs."""
    try:
        table_name, column = DIMENSIONS[dimension]
    except KeyError as exc:
        raise ValueError(f"Dimensión no admitida: {dimension}") from exc

    bridge = views[table_name]
    ids = bridge.loc[bridge[column].eq(category), "content_id"].unique()
    return selected.loc[selected["content_id"].isin(ids)].copy()


def segment_metrics(segment: pd.DataFrame, views: dict[str, object]) -> dict[str, float | int]:
    """Calculate comparison metrics with their business-rule eligibility applied."""
    reliable_popularity_ids = set(views["catalogo_popularity"]["content_id"])
    popularity = segment.loc[
        segment["content_id"].isin(reliable_popularity_ids), "popularity"
    ]
    rated = segment.loc[segment["vote_count"].gt(0), "vote_average"]
    return {
        "titles": int(segment["content_id"].nunique()),
        "movies": int(segment["type"].eq("Movie").sum()),
        "tv_shows": int(segment["type"].eq("TV Show").sum()),
        "median_popularity": float(popularity.median()) if not popularity.empty else float("nan"),
        "mean_rating": float(rated.mean()) if not rated.empty else float("nan"),
        "rated_titles": int(rated.shape[0]),
    }


def compare_segments(
    selected: pd.DataFrame,
    views: dict[str, object],
    *,
    dimension: str,
    left_category: str,
    right_category: str,
) -> pd.DataFrame:
    """Return left/right metrics and the left-minus-right difference."""
    left = segment_metrics(
        segment_selection(selected, views, dimension=dimension, category=left_category),
        views,
    )
    right = segment_metrics(
        segment_selection(selected, views, dimension=dimension, category=right_category),
        views,
    )
    rows = []
    for metric in left:
        left_value, right_value = left[metric], right[metric]
        difference = (
            float("nan")
            if pd.isna(left_value) or pd.isna(right_value)
            else left_value - right_value
        )
        rows.append(
            {
                "metric": metric,
                "left": left_value,
                "right": right_value,
                "difference": difference,
            }
        )
    return pd.DataFrame(rows)
