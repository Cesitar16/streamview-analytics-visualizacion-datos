"""StreamView EP2: executive and acquisition dashboards.

Run from the repository root with ``uv run streamlit run dashboard/app.py``.
"""

import json
import sys
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dashboard_data import (  # noqa: E402
    category_counts,
    country_performance,
    financial_selection,
    financial_summary,
    genre_performance,
    load_views,
    select_catalog,
)


st.set_page_config(page_title="StreamView | Análisis del catálogo", page_icon="🎬", layout="wide", initial_sidebar_state="auto")
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px;}
    .sv-brand {font-size:.8rem;font-weight:800;letter-spacing:.16em;color:#167b87;margin-bottom:.45rem}
    .sv-title {font-size:2.15rem;font-weight:750;letter-spacing:-.035em;line-height:1.1;color:#172b45;margin:0}
    .sv-subtitle {font-size:.96rem;color:#566981;margin:.7rem 0 1.3rem}
    .sv-section {font-size:1.28rem;font-weight:730;color:#172b45;margin:1.3rem 0 .25rem}
    .sv-note {background:#e9f4f5;border-left:4px solid #168b91;border-radius:7px;
      color:#254759;padding:.8rem 1rem;margin:.7rem 0 1.2rem;font-size:.9rem}
    div[data-testid="stMetric"] {background:#fff;border:1px solid #dde6f0;
      padding:1rem 1.1rem;border-radius:12px;box-shadow:0 2px 9px rgba(24,46,73,.035);min-height:102px}
    div[data-testid="stMetric"] label {font-weight:600;color:#526681}
    div[data-testid="stMetricValue"] {color:#173552;font-weight:700;letter-spacing:-.035em}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > div[data-testid="stPlotlyChart"]) {border-radius:12px}
    section[data-testid="stSidebar"] {border-right:1px solid #dbe5ef}
    section[data-testid="stSidebar"] .block-container {padding-top:1.3rem}
    .sv-sidebar-title {font-size:1.1rem;font-weight:750;color:#173552;margin:0 0 .2rem}
    .sv-sidebar-help {font-size:.8rem;color:#607189;margin-bottom:.8rem}
    </style>
    """,
    unsafe_allow_html=True,
)

COLORS = {"Movie": "#2875b9", "TV Show": "#17a398"}
TEMPLATE = "plotly_white"


def number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def decimal(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def section(title: str, description: str | None = None):
    st.markdown(f'<div class="sv-section">{title}</div>', unsafe_allow_html=True)
    if description:
        st.caption(description)


def metric(column, label: str, value: str, help_text: str | None = None):
    column.metric(label, value, help=help_text)


@st.cache_data(show_spinner="Preparando catálogo oficial…")
def cached_views():
    return load_views()


def chart(fig: go.Figure, *, height: int = 400, note: str | None = None):
    title = fig.layout.title.text if fig.layout.title else None
    fig.update_layout(
        template=TEMPLATE,
        title=None,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#344861", size=12),
        height=height,
        margin=dict(l=18, r=18, t=22, b=16),
        legend_title_text="",
        coloraxis_colorbar=dict(title=""),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf1f5", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    with st.container(border=True):
        if title:
            st.markdown(f"**{title}**")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "displayModeBar": False})
        if note:
            st.caption(note)


def d3_treemap(data: pd.DataFrame, selected_titles: int):
    payload = json.dumps(
        {"records": [{"name": str(row.genre), "value": int(row.titles)} for row in data.itertuples()],
         "selectedTitles": selected_titles},
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    html = (ROOT / "dashboard/d3_treemap.html").read_text(encoding="utf-8")
    d3_source = (ROOT / "dashboard/d3.v7.min.js").read_text(encoding="utf-8")
    st.iframe(html.replace("__DATA__", payload).replace("__D3__", d3_source), height=590)


try:
    views = cached_views()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

catalog = views["catalogo_general"]
genre_values = sorted(views["catalogo_generos"]["genre"].dropna().unique().tolist())
country_values = sorted(views["catalogo_paises"]["country"].dropna().unique().tolist())
language_values = sorted(catalog["language"].dropna().unique().tolist())

st.markdown('<div class="sv-brand">STREAMVIEW  /  ANALÍTICA AUDIOVISUAL</div>', unsafe_allow_html=True)
st.markdown('<div class="sv-title">StreamView · Del catálogo a la decisión</div>', unsafe_allow_html=True)
st.markdown('<div class="sv-subtitle">Explora la oferta, compara señales de audiencia y evalúa la cobertura financiera del caso académico.</div>', unsafe_allow_html=True)
page = st.segmented_control(
    "Perspectiva", ["Panorama del catálogo", "Contenidos y adquisición"],
    default="Panorama del catálogo", key="sv_page",
)
executive = page == "Panorama del catálogo"


def reset_filters():
    for key in ("sv_types", "sv_years", "sv_genres", "sv_countries", "sv_languages", "sv_rating",
                "sv_min_votes", "sv_min_country"):
        st.session_state.pop(key, None)


with st.sidebar:
    st.markdown('<div class="sv-sidebar-title">Explorar el catálogo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sv-sidebar-help">Los gráficos responden a tu selección.</div>', unsafe_allow_html=True)
    st.button("Restablecer filtros", on_click=reset_filters, width="stretch")
    st.markdown("**Contenido**")
    types = st.multiselect("Tipo", ["Movie", "TV Show"], format_func=lambda x: "Película" if x == "Movie" else "Serie", key="sv_types", placeholder="Todos los tipos")
    years = st.slider("Año de estreno", 2010, 2025, (2010, 2025), key="sv_years")
    genres = st.multiselect("Género", genre_values, key="sv_genres", placeholder="Todos los géneros")
    if not executive:
        st.markdown("**Origen y valoración**")
        countries = st.multiselect("País de producción", country_values, key="sv_countries", placeholder="Todos los países")
        languages = st.multiselect("Idioma", language_values, key="sv_languages", placeholder="Todos los idiomas")
        rating_range = st.slider("Calificación", 0.0, 10.0, (0.0, 10.0), 0.1, key="sv_rating")
        with st.expander("Criterios para rankings y mapa"):
            min_votes = st.slider("Votos mínimos para títulos", 1, 1000, 100, key="sv_min_votes")
            min_country = st.slider("Títulos mínimos por país", 20, 500, 100, 10, key="sv_min_country")
    else:
        countries, languages, rating_range = [], [], None
        st.caption("Origen y valoración se filtran en Contenidos y adquisición. Sus selecciones se conservan al volver a esa vista.")
selected = select_catalog(
    views, types=types, years=years, genres=genres, countries=countries,
    languages=languages, rating_range=rating_range,
)
selected_ids = set(selected["content_id"])
active_filters = sum([bool(types), years != (2010, 2025), bool(genres), bool(countries), bool(languages),
                      rating_range is not None and rating_range != (0.0, 10.0)])
st.markdown(
    f'<div class="sv-note"><strong>{number(len(selected))} títulos seleccionados</strong> · '
    f'Estrenos {years[0]}–{years[1]} · {active_filters} filtros activos. '
    'La selección actualiza indicadores y visualizaciones de esta perspectiva.</div>',
    unsafe_allow_html=True,
)
filter_details = []
if types:
    filter_details.append("Tipo: " + ", ".join("Película" if value == "Movie" else "Serie" for value in types))
if years != (2010, 2025):
    filter_details.append(f"Estreno: {years[0]}–{years[1]}")
for label, values in (("Género", genres), ("País", countries), ("Idioma", languages)):
    if values:
        filter_details.append(f"{label}: " + ", ".join(map(str, values)))
if rating_range is not None and rating_range != (0.0, 10.0):
    filter_details.append(f"Calificación: {decimal(rating_range[0])}–{decimal(rating_range[1])}")
st.caption("Filtros aplicados: " + (" · ".join(escape(item) for item in filter_details) if filter_details else "ninguno"))
if selected.empty:
    st.warning("No hay contenidos para esta combinación. Amplía el período o quita un filtro para seguir explorando.")
    st.button("Restablecer y ver todo el catálogo", on_click=reset_filters)
    st.stop()

genre_counts = category_counts(selected, views["catalogo_generos"], "genre")
country_counts = category_counts(selected, views["catalogo_paises"], "country")

if executive:
    section("Panorama del catálogo", "Composición, evolución y procedencia de los contenidos seleccionados.")
    cols = st.columns(4)
    metric(cols[0], "Títulos", number(len(selected)))
    metric(cols[1], "Películas", number(selected['type'].eq('Movie').sum()))
    metric(cols[2], "Series", number(selected['type'].eq('TV Show').sum()))
    metric(cols[3], "Países representados", number(len(country_counts)))
    cols = st.columns(4)
    metric(cols[0], "Idiomas", number(selected['language'].nunique()))
    metric(cols[1], "Géneros", number(len(genre_counts)))
    popularity = selected.loc[
        selected["content_id"].isin(views["catalogo_popularity"]["content_id"]),
        "popularity",
    ]
    metric(cols[2], "Popularidad media", decimal(popularity.mean()))
    rated = selected.loc[selected["vote_count"].gt(0), "vote_average"]
    metric(cols[3], "Calificación media", f"{decimal(rated.mean(), 2)} / 10")

    section("Años registrados y composición", "Los años describen la distribución de la fuente; las barras comparan tipos de contenido.")

    left, right = st.columns(2)
    with left:
        releases = selected.groupby("release_year", as_index=False).agg(titles=("content_id", "nunique"))
        fig = px.bar(releases, x="release_year", y="titles", title="Títulos por año de estreno registrado",
                     labels={"release_year": "Año de estreno", "titles": "Contenidos"},
                     color_discrete_sequence=["#2875b9"])
        fig.update_xaxes(type="category")
        chart(fig, note="La fuente contiene cerca de 2.000 títulos por año y repite el año de estreno como año de incorporación. No permite inferir altas reales ni una tendencia del mercado.")
    with right:
        type_counts = selected.groupby("type", as_index=False).agg(titles=("content_id", "nunique"))
        type_counts["label"] = type_counts["titles"].map(number)
        fig = px.bar(type_counts, x="type", y="titles", color="type", color_discrete_map=COLORS,
                     title="Películas frente a series", labels={"type": "Tipo", "titles": "Contenidos"}, text="label")
        fig.update_layout(showlegend=False)
        chart(fig)
        if len(type_counts) == 2:
            movie_total = int(type_counts.loc[type_counts["type"].eq("Movie"), "titles"].iloc[0])
            show_total = int(type_counts.loc[type_counts["type"].eq("TV Show"), "titles"].iloc[0])
            st.caption(f"Diferencia: {number(abs(movie_total - show_total))} títulos · "
                       f"películas {decimal(100 * movie_total / len(selected), 2)} %; "
                       f"series {decimal(100 * show_total / len(selected), 2)} %.")

    section("Origen y géneros", "Un mismo título puede tener más de un país o género asociado.")
    left, right = st.columns(2)
    with left:
        top = country_counts.head(10).sort_values("titles")
        fig = px.bar(top, x="titles", y="country", orientation="h", title="Diez países con más producciones",
                     labels={"titles": "Contenidos", "country": "País"}, color_discrete_sequence=["#2875b9"])
        chart(fig)
    with right:
        with st.container(border=True):
            st.markdown("**Géneros por volumen**")
            st.caption("El área representa títulos asociados. Haz clic o usa la lista para consultar géneros pequeños.")
            d3_treemap(genre_counts, len(selected))

    language_counts = (
        selected.dropna(subset=["language"])
        .groupby("language", as_index=False)
        .agg(titles=("content_id", "nunique"))
        .nlargest(10, "titles")
        .sort_values("titles")
    )
    fig = px.bar(language_counts, x="titles", y="language", orientation="h",
                 title="Diez idiomas más representados", labels={"titles": "Contenidos", "language": "Código de idioma"},
                 color_discrete_sequence=["#17a398"])
    chart(fig)

    geo = country_counts.copy()
    fig = px.choropleth(geo, locations="country", locationmode="country names", color="titles",
                        hover_name="country", title="Producciones asociadas por país",
                        color_continuous_scale="Teal", labels={"titles": "Contenidos"})
    fig.update_geos(showframe=False, showcoastlines=True, projection_type="natural earth")
    chart(fig, height=490)
    st.caption("Un título puede tener varios países y géneros; por eso estos recuentos no suman el total. La cobertura del mapa depende de los nombres geográficos reconocidos.")

else:
    section("Contenidos y adquisición", "Compara interés, valoración, créditos y desempeño financiero dentro de la selección.")
    cols = st.columns(4)
    metric(cols[0], "Títulos", number(len(selected)))
    metric(cols[1], "Con votos", number(selected['vote_count'].gt(0).sum()))
    metric(cols[2], "Popularidad mediana", decimal(selected['popularity'].median()))
    metric(cols[3], "Calificación media", f"{decimal(selected.loc[selected['vote_count'].gt(0), 'vote_average'].mean(), 2)} / 10")

    eligible = selected.loc[
        selected["content_id"].isin(views["catalogo_popularity"]["content_id"])
        & selected["vote_count"].gt(0)
    ].copy()
    section("Señales para elegir contenidos", "La popularidad y la calificación miden aspectos distintos. El tamaño de cada punto refleja la cantidad de votos.")
    left, right = st.columns(2)
    with left:
        if eligible.empty:
            st.info("Ningún título de la selección tiene popularidad válida y votos para esta comparación.")
        else:
            fig = px.scatter(eligible, x="popularity", y="vote_average", color="type",
                             size="vote_count", size_max=12, hover_name="title",
                             hover_data={"vote_count": True, "popularity": ":.1f", "vote_average": ":.2f"},
                             log_x=True, color_discrete_map=COLORS, render_mode="webgl",
                             title="Popularidad y calificación son señales distintas",
                             labels={"popularity": "Índice de popularidad · escala log", "vote_average": "Calificación / 10", "type": "Tipo"})
            fig.update_traces(marker=dict(opacity=0.35, line=dict(width=0)))
            chart(fig, height=460)
    with right:
        performance = genre_performance(selected, views)
        top_perf = performance.loc[performance["titles"].ge(30)].nlargest(12, "median_popularity")
        popularity_tab, rating_tab = st.tabs(["Popularidad", "Calificación"])
        with popularity_tab:
            if top_perf.empty:
                st.info("Ningún género alcanza el mínimo de 30 títulos con popularidad válida en esta selección.")
            else:
                fig = px.bar(top_perf.sort_values("median_popularity"), x="median_popularity", y="genre",
                             orientation="h", title="Popularidad mediana por género",
                             hover_data=["titles"], labels={"median_popularity": "Popularidad mediana", "genre": "Género"},
                             color_discrete_sequence=["#2875b9"])
                chart(fig, height=420, note="Incluye títulos con índice de popularidad válido; mínimo 30 títulos por género.")
        with rating_tab:
            top_ratings = performance.loc[performance["rated_titles"].ge(100)].nlargest(12, "mean_rating").sort_values("mean_rating")
            if top_ratings.empty:
                st.info("Ningún género alcanza el mínimo de 100 títulos valorados en esta selección.")
            else:
                fig = px.scatter(top_ratings, x="mean_rating", y="genre", size="rated_titles", size_max=14,
                                 title="Calificación media por género",
                                 hover_data={"rated_titles": True, "mean_rating": ":.2f"},
                                 labels={"mean_rating": "Calificación media / 10", "genre": "Género", "rated_titles": "Títulos con votos"},
                                 color_discrete_sequence=["#17a398"])
                lower = max(0, top_ratings["mean_rating"].min() - 0.3)
                upper = min(10, top_ratings["mean_rating"].max() + 0.3)
                fig.update_xaxes(range=[lower, upper])
                chart(fig, height=420, note="Eje acotado para distinguir notas cercanas; consulta el valor y la cantidad de títulos al pasar el cursor.")
    with st.container(border=True):
        st.markdown("**Géneros por volumen de contenidos**")
        st.caption("El área de cada bloque representa títulos asociados; las categorías pueden superponerse.")
        d3_treemap(genre_counts, len(selected))

    section("Rankings y cobertura", "Los rankings usan los umbrales definidos en el panel lateral.")
    left, right = st.columns(2)
    with left:
        top_rated = selected.loc[selected["vote_count"].ge(min_votes)].sort_values(
            ["vote_average", "vote_count", "title"], ascending=[False, False, True]
        ).head(10)[["title", "type", "vote_average", "vote_count"]]
        with st.container(border=True):
            st.markdown(f"**Diez títulos mejor evaluados · ≥ {min_votes} votos**")
            if top_rated.empty:
                st.info("Ningún título alcanza el mínimo de votos. Reduce el umbral en el panel lateral.")
            st.dataframe(top_rated, hide_index=True, width="stretch", height=385,
                         column_config={"title": "Título", "type": "Tipo", "vote_average": st.column_config.NumberColumn("Nota", format="%.2f"), "vote_count": st.column_config.NumberColumn("Votos", format="%d")})
    with right:
        top_directors = category_counts(selected, views["catalogo_directores"], "director").head(10)
        top_actors = category_counts(selected, views["catalogo_cast"], "actor").head(10)
        with st.container(border=True):
            st.markdown("**Personas con más títulos**")
            tabs = st.tabs(["Directores", "Intérpretes"])
            with tabs[0]:
                st.dataframe(top_directors, hide_index=True, width="stretch", height=310,
                             column_config={"director": "Director", "titles": "Títulos"})
            with tabs[1]:
                st.dataframe(top_actors, hide_index=True, width="stretch", height=310,
                             column_config={"actor": "Intérprete", "titles": "Títulos"})
            st.caption("Los créditos informados tienen cobertura parcial, especialmente en series.")

    geo = country_performance(selected, views, min_country)
    if geo.empty:
        st.info(f"Ningún país alcanza {min_country} títulos valorados. Reduce el umbral en el panel lateral.")
    else:
        fig = px.choropleth(geo, locations="country", locationmode="country names", color="mean_rating",
                            hover_name="country", hover_data={"titles": True},
                            title=f"Calificación media por país · mínimo {min_country} títulos valorados",
                            range_color=(0, 10), color_continuous_scale="Teal",
                            labels={"mean_rating": "Calificación media"})
        fig.update_geos(showframe=False, showcoastlines=True, projection_type="natural earth")
        chart(fig, height=490)
        top_countries = geo.nlargest(10, "mean_rating").sort_values("mean_rating")
        ranking = px.scatter(top_countries, x="mean_rating", y="country", size="titles", size_max=15,
                             title="Países con mayor calificación media",
                             hover_data={"titles": True, "mean_rating": ":.2f"},
                             labels={"mean_rating": "Calificación media / 10", "country": "País", "titles": "Títulos valorados"},
                             color_discrete_sequence=["#2875b9"])
        ranking.update_xaxes(range=[max(0, top_countries["mean_rating"].min() - 0.3),
                                     min(10, top_countries["mean_rating"].max() + 0.3)])
        chart(ranking, height=400, note="Eje acotado y mínimo de cobertura aplicados; el tamaño indica títulos valorados.")

    section("Películas · análisis financiero", "Solo películas con presupuesto e ingresos positivos e informados.")
    finance = financial_selection(selected, views)
    summary = financial_summary(finance)
    movie_count = int(selected['type'].eq('Movie').sum())
    coverage = 100 * summary['eligible_movies'] / movie_count if movie_count else 0
    st.markdown(
        f'<div class="sv-note"><strong>Cobertura financiera: {number(summary["eligible_movies"])} de '
        f'{number(movie_count)} películas ({decimal(coverage)} %).</strong> '
        'Interpreta estos resultados como una muestra parcial.</div>', unsafe_allow_html=True,
    )
    st.caption("Ingresos / presupuesto es un múltiplo bruto, no utilidad neta ni rentabilidad porcentual. Montos en USD según la documentación EP1.")
    cols = st.columns(2)
    metric(cols[0], "Presupuesto total", f"US$ {decimal(summary['total_budget']/1e9, 2)} mil M")
    metric(cols[1], "Ingresos totales", f"US$ {decimal(summary['total_revenue']/1e9, 2)} mil M")
    cols = st.columns(3)
    metric(cols[0], "Películas elegibles", number(summary['eligible_movies']))
    metric(cols[1], "Presupuesto medio", f"US$ {decimal(summary['average_budget']/1e6)} M")
    metric(cols[2], "Ingresos / presupuesto", f"{decimal(summary['portfolio_multiple'], 2)}×")
    if finance.empty:
        st.info("La selección actual no contiene películas con datos financieros elegibles.")
    else:
        left, right = st.columns(2)
        with left:
            finance_plot = finance.assign(coverage_status=finance["revenue"].ge(finance["budget"]).map(
                {True: "Cubre presupuesto", False: "No cubre presupuesto"}))
            fig = px.scatter(finance_plot, x="budget", y="revenue", color="coverage_status", hover_name="title",
                             log_x=True, log_y=True,
                             color_discrete_map={"Cubre presupuesto": "#187A75", "No cubre presupuesto": "#D76B5C"},
                             hover_data={"return_multiple": ":.2f"},
                             title="Presupuesto frente a ingresos · escala logarítmica",
                             labels={"budget": "Presupuesto · USD", "revenue": "Ingresos · USD",
                                     "return_multiple": "Ingresos / presupuesto", "coverage_status": "Cobertura"})
            reference_start = min(finance["budget"].min(), finance["revenue"].min())
            reference_end = max(finance["budget"].max(), finance["revenue"].max())
            fig.add_scatter(x=[reference_start, reference_end], y=[reference_start, reference_end],
                            mode="lines", name="Ingresos = presupuesto", line=dict(color="#ba5960", dash="dash"),
                            hoverinfo="skip")
            chart(fig, height=440)
        with right:
            top_revenue = finance.nlargest(10, "revenue").sort_values("revenue")
            fig = px.bar(top_revenue, x="revenue", y="title", orientation="h", title="Diez películas con mayores ingresos",
                         labels={"revenue": "Ingresos · USD", "title": "Película"}, color_discrete_sequence=["#17a398"])
            chart(fig, height=440)
        st.caption(f"Múltiplo mediano por película: {decimal(summary['median_title_multiple'], 2)}×. Los valores extremos pueden deberse a presupuestos registrados muy pequeños.")
        with st.expander("Examinar las 10 películas con mayor múltiplo de ingresos"):
            st.dataframe(
                finance.nlargest(10, "return_multiple")[["title", "budget", "revenue", "return_multiple"]],
                hide_index=True, width="stretch",
                column_config={"title": "Título", "budget": st.column_config.NumberColumn("Presupuesto · USD", format="$%,.0f"),
                               "revenue": st.column_config.NumberColumn("Ingresos · USD", format="$%,.0f"),
                               "return_multiple": st.column_config.NumberColumn("Múltiplo", format="%.2f×")},
            )
        budget_limit = float(finance["budget"].quantile(0.25))
        return_limit = float(finance["return_multiple"].quantile(0.75))
        candidates = finance.loc[
            finance["budget"].le(budget_limit) & finance["return_multiple"].ge(return_limit)
        ].sort_values("return_multiple", ascending=False)
        section("Candidatas para revisar", "Bajo presupuesto y alto múltiplo relativo dentro de la selección filtrada.")
        st.caption(
            f"Criterio dentro de la selección: presupuesto ≤ P25 (US$ {budget_limit:,.0f}) "
            f"y múltiplo ≥ P75 ({return_limit:,.2f}×). Cumplen {len(candidates):,} películas."
        )
        st.dataframe(candidates[["title", "budget", "revenue", "return_multiple"]].head(30),
                     hide_index=True, width="stretch",
                     column_config={"title": "Título", "budget": st.column_config.NumberColumn("Presupuesto · USD", format="$%,.0f"),
                                    "revenue": st.column_config.NumberColumn("Ingresos · USD", format="$%,.0f"),
                                    "return_multiple": st.column_config.NumberColumn("Múltiplo", format="%.2f×")})

st.divider()
section("Lleva la selección a tu análisis", "Descarga los registros visibles para revisar títulos concretos.")
st.download_button(
    "Descargar catálogo filtrado (CSV)",
    data=selected.to_csv(index=False).encode("utf-8-sig"),
    file_name="streamview_catalogo_filtrado.csv",
    mime="text/csv",
)
if not executive:
    st.download_button(
        "Descargar películas financieras filtradas (CSV)",
        data=finance.to_csv(index=False).encode("utf-8-sig"),
        file_name="streamview_finanzas_filtradas.csv",
        mime="text/csv",
    )
st.caption("Fuente: Netflix Movies Detailed up to 2025 y Netflix TV Shows Detailed up to 2025, entregados para StreamView. Las métricas provienen de las vistas procesadas en EP1. La clasificación etaria no está disponible: el campo rating replica la calificación numérica.")
