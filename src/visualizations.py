"""Visualizaciones reutilizables del análisis StreamView."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


TYPE_COLORS = {"Movie": "#2F6690", "TV Show": "#D17A22"}


def plot_popularity_comparison(
    popularity_summary: pd.DataFrame,
) -> Figure:
    """Compara medianas e intervalos intercuartílicos de popularidad por tipo."""
    data = popularity_summary.sort_values("type").reset_index(drop=True)
    colors = [TYPE_COLORS.get(value, "#6C757D") for value in data["type"]]
    lower = data["median_popularity"] - data["q1_popularity"]
    upper = data["q3_popularity"] - data["median_popularity"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        data["type"], data["median_popularity"], color=colors, width=0.58
    )
    ax.errorbar(
        data["type"],
        data["median_popularity"],
        yerr=[lower, upper],
        fmt="none",
        ecolor="#222222",
        capsize=7,
        linewidth=1.8,
    )
    ratio = data["median_popularity"].max() / data["median_popularity"].min()
    ax.set_title(
        f"Las series alcanzan {ratio:.1f} veces la popularidad mediana de las películas"
    )
    ax.set_xlabel("Tipo de contenido")
    ax.set_ylabel("Índice de popularidad (escala logarítmica)")
    ax.set_yscale("log")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, data["median_popularity"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f" {value:.2f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    fig.tight_layout()
    return fig


def plot_rating_comparison(rating_summary: pd.DataFrame) -> Figure:
    """Distingue calidad de valoración, cobertura y volumen de votos."""
    data = rating_summary.sort_values("type").reset_index(drop=True)
    colors = [TYPE_COLORS.get(value, "#6C757D") for value in data["type"]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    rating_bars = axes[0].bar(
        data["type"], data["median_vote_average"], color=colors, width=0.58
    )
    axes[0].set_title("Calidad: valoración mediana")
    axes[0].set_ylabel("vote_average (0–10)")
    axes[0].set_ylim(0, 10)
    for bar, score, coverage in zip(
        rating_bars, data["median_vote_average"], data["rating_coverage_pct"]
    ):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            score,
            f"{score:.2f}\nCobertura {coverage:.1f}%",
            ha="center",
            va="bottom",
        )

    vote_bars = axes[1].bar(
        data["type"], data["median_vote_count"], color=colors, width=0.58
    )
    axes[1].set_title("Cantidad: votos medianos")
    axes[1].set_ylabel("vote_count (escala logarítmica)")
    axes[1].set_yscale("log")
    for bar, votes in zip(vote_bars, data["median_vote_count"]):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            votes,
            f" {votes:,.1f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    for ax in axes:
        ax.set_xlabel("Tipo de contenido")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Las series puntúan más alto; las películas concentran más votos")
    fig.tight_layout()
    return fig


def plot_popularity_rating_relationship(
    catalogo_popularity: pd.DataFrame,
    association_summary: pd.DataFrame,
) -> Figure:
    """Visualiza popularity vs vote_average por tipo y reporta rho de Spearman."""
    eligible = catalogo_popularity.loc[
        catalogo_popularity["vote_count"].gt(0)
        & catalogo_popularity["vote_average"].notna()
        & catalogo_popularity["popularity"].notna()
    ]
    content_types = sorted(eligible["type"].unique())
    fig, axes = plt.subplots(1, len(content_types), figsize=(13, 5), sharey=True)
    if len(content_types) == 1:
        axes = [axes]
    rho_by_scope = association_summary.set_index("scope")["spearman_rho"]
    for ax, content_type in zip(axes, content_types):
        group = eligible.loc[eligible["type"] == content_type]
        ax.scatter(
            group["popularity"],
            group["vote_average"],
            s=12,
            alpha=0.16,
            color=TYPE_COLORS.get(content_type, "#6C757D"),
            edgecolors="none",
        )
        ax.set_xscale("log")
        ax.set_title(f"{content_type} · ρ={rho_by_scope.loc[content_type]:.3f}")
        ax.set_xlabel("popularity (escala logarítmica)")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("vote_average")
    axes[0].set_ylim(0, 10.2)
    fig.suptitle("Popularidad y valoración apenas se relacionan dentro de cada formato")
    fig.tight_layout()
    return fig


def plot_top_popular_contents(top_popularity: pd.DataFrame) -> Figure:
    """Presenta un ranking ejecutivo de los contenidos con mayor popularity."""
    data = top_popularity.sort_values("popularity").copy()
    labels = data["title"].map(
        lambda value: value if len(value) <= 38 else f"{value[:35]}..."
    )
    colors = [TYPE_COLORS.get(value, "#6C757D") for value in data["type"]]
    type_counts = data["type"].value_counts()
    dominant_type = type_counts.index[0]
    dominant_count = int(type_counts.iloc[0])
    dominant_label = "TV Shows" if dominant_type == "TV Show" else "Movies"

    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars = ax.barh(labels, data["popularity"], color=colors)
    ax.set_title(
        f"{dominant_label} ocupan {dominant_count} de los {len(data)} primeros lugares de popularidad"
    )
    ax.set_xlabel("Índice de popularidad")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.22)
    for bar, value in zip(bars, data["popularity"]):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {value:,.0f}",
            va="center",
        )
    handles = [
        plt.Line2D([0], [0], color=color, linewidth=8, label=content_type)
        for content_type, color in TYPE_COLORS.items()
    ]
    ax.legend(handles=handles, title="Formato", loc="lower right")
    fig.tight_layout()
    return fig


def plot_genre_popularity(popularity_by_genre: pd.DataFrame, top_n: int = 10) -> Figure:
    """Compara la popularidad mediana de los géneros líderes."""
    eligible = popularity_by_genre.loc[
        popularity_by_genre["genre"].astype("string").str.casefold().ne("unknown")
    ]
    data = eligible.head(top_n).sort_values("median_popularity")
    leader = eligible.iloc[0]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(data["genre"], data["median_popularity"], color="#4C956C")
    ax.set_title(
        f"{leader['genre']} lidera la popularidad mediana por género"
    )
    ax.set_xlabel("Popularidad mediana")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.22)
    for bar, value in zip(bars, data["median_popularity"]):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f" {value:.1f}",
            va="center",
        )
    fig.text(
        0.01,
        0.01,
        "Nota: ‘Unknown’ se conserva en la tabla analítica y se excluye solo de esta visualización.",
        fontsize=9,
        color="#4A4A4A",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def plot_historical_evolution(evolution: pd.DataFrame) -> Figure:
    """Compara evolución anual por release_year entre Movies y TV Shows."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    for content_type, group in evolution.groupby("type", sort=True):
        color = TYPE_COLORS.get(content_type, "#6C757D")
        axes[0].plot(
            group["release_year"],
            group["median_popularity"],
            marker="o",
            linewidth=2,
            label=content_type,
            color=color,
        )
        axes[1].plot(
            group["release_year"],
            group["median_vote_average"],
            marker="o",
            linewidth=2,
            label=content_type,
            color=color,
        )
    fig.suptitle(
        "Las trayectorias difieren por formato y sus máximos ocurren en años distintos"
    )
    axes[0].set_title("Popularidad mediana por año de estreno")
    axes[0].set_ylabel("Popularidad mediana (escala log)")
    axes[0].set_yscale("log")
    axes[1].set_title("Evolución de valoración mediana entre títulos con votos")
    axes[1].set_ylabel("vote_average mediana")
    axes[1].set_xlabel("Año de estreno (release_year)")
    axes[1].set_ylim(0, 10)
    axes[1].set_xticks(sorted(evolution["release_year"].unique()))
    axes[1].tick_params(axis="x", rotation=45)
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(title="Tipo")
    fig.tight_layout()
    return fig
