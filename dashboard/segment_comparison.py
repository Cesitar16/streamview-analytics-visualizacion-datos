"""Streamlit presentation for the catalogue segment comparator."""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.segment_comparison import compare_segments


METRIC_LABELS = {
    "titles": "Títulos únicos",
    "movies": "Películas",
    "tv_shows": "Series",
    "median_popularity": "Popularidad mediana",
    "mean_rating": "Calificación media / 10",
    "rated_titles": "Contenidos con votos",
}


def _number(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_segment_comparison(selected, views, *, colors: dict[str, str], chart) -> None:
    """Render a genre-only comparison within the current global selection."""
    choices = sorted(views["catalogo_generos"]["genre"].dropna().unique())
    if len(choices) < 2:
        return

    st.markdown("<div class='sv-section'>Comparador estratégico de géneros</div>", unsafe_allow_html=True)
    st.caption(
        "Contrasta dos géneros dentro de los filtros actuales. Un título puede aparecer en ambos grupos; "
        "por eso los recuentos no se suman para estimar el total del catálogo."
    )
    left_column, right_column = st.columns(2)
    with left_column:
        left_category = st.selectbox("Género A", choices, index=choices.index("Drama") if "Drama" in choices else 0,
                                     key="sv_compare_left")
    default_right = "Comedy" if "Comedy" in choices else choices[1]
    with right_column:
        right_category = st.selectbox("Género B", choices, index=choices.index(default_right), key="sv_compare_right")

    comparison = compare_segments(
        selected,
        views,
        dimension="genre",
        left_category=left_category,
        right_category=right_category,
    )
    metrics = comparison.set_index("metric")
    cards = st.columns(3)
    for column, metric_name in zip(cards, ("titles", "median_popularity", "mean_rating"), strict=True):
        row = metrics.loc[metric_name]
        difference = row["difference"]
        column.metric(
            METRIC_LABELS[metric_name],
            f"{left_category}: {_number(row['left'], 0 if metric_name == 'titles' else 2)}",
            delta=(
                "Sin diferencia disponible"
                if pd.isna(difference)
                else f"{_number(difference, 0 if metric_name == 'titles' else 2)} vs. {right_category}"
            ),
            help="La variación es Género A menos Género B.",
        )

    composition = comparison.loc[comparison["metric"].isin(["movies", "tv_shows"])].copy()
    composition["metric"] = composition["metric"].map(METRIC_LABELS)
    long = composition.melt(id_vars="metric", value_vars=["left", "right"], var_name="segment", value_name="titles")
    long["segment"] = long["segment"].map({"left": left_category, "right": right_category})
    figure = px.bar(
        long,
        x="metric",
        y="titles",
        color="segment",
        barmode="group",
        color_discrete_map={left_category: colors["Movie"], right_category: colors["TV Show"]},
        title="Composición por tipo de contenido",
        labels={"metric": "", "titles": "Títulos únicos", "segment": "Género"},
    )
    chart(figure, height=360, note="La comparación usa títulos únicos y conserva los filtros generales de la página.")
