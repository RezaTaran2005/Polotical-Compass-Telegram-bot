

from __future__ import annotations

import io

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


matplotlib.use("Agg")


_QUADRANT_COLORS = {
    "top_right":    "#89C5F6",   # Right-Authoritarian  (red)
    "top_left":     "#FF83BA",   # Left-Authoritarian   (teal)
    "bottom_right": "#C8B8FF",   # Right-Libertarian    (mint)
    "bottom_left":  "#B3E5B3",   # Left-Libertarian     (yellow)
}
_AXIS_COLOR      = "#1a1a2e"
_GRID_COLOR      = "#aaaaaa"
_POINT_COLOR     = "#e63946"
_POINT_EDGE      = "#6b0000"
_BG_COLOR        = "#f8f9fa"
_TITLE_COLOR     = "#1a1a2e"
_LABEL_COLOR     = "#2d2d2d"


def generate_compass_image(x: float, y: float) -> bytes:

    fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
    fig.patch.set_facecolor(_BG_COLOR)
    ax.set_facecolor(_BG_COLOR)

    ax.fill_between([0, 10],  0,  10, color=_QUADRANT_COLORS["top_right"],    alpha=0.35)
    ax.fill_between([-10, 0], 0,  10, color=_QUADRANT_COLORS["top_left"],     alpha=0.35)
    ax.fill_between([0, 10], -10,  0, color=_QUADRANT_COLORS["bottom_right"], alpha=0.35)
    ax.fill_between([-10, 0], -10, 0, color=_QUADRANT_COLORS["bottom_left"],  alpha=0.35)

    ax.set_xlim(-10.5, 10.5)
    ax.set_ylim(-10.5, 10.5)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.grid(color=_GRID_COLOR, linestyle="--", linewidth=0.6, alpha=0.55, zorder=1)

    ax.axhline(0, color=_AXIS_COLOR, linewidth=2.0, zorder=2)
    ax.axvline(0, color=_AXIS_COLOR, linewidth=2.0, zorder=2)

    for spine in ax.spines.values():
        spine.set_edgecolor("#cccccc")
        spine.set_linewidth(0.8)

    _label_kwargs = dict(fontsize=11, ha="center", va="center",
                         fontweight="bold", color=_LABEL_COLOR, alpha=0.75)
    ax.text( 5.5,  5.5, "Right\nAuthoritarian", **_label_kwargs)
    ax.text(-5.5,  5.5, "Left\nAuthoritarian",  **_label_kwargs)
    ax.text( 5.5, -5.5, "Right\nLibertarian",   **_label_kwargs)
    ax.text(-5.5, -5.5, "Left\nLibertarian",    **_label_kwargs)

    arrow_style = dict(arrowstyle="->", color=_AXIS_COLOR, lw=1.5)
    ax.annotate("", xy=(10.3, 0), xytext=(9.8, 0),
                 arrowprops=arrow_style, zorder=3)
    ax.annotate("", xy=(-10.3, 0), xytext=(-9.8, 0),
                 arrowprops=arrow_style, zorder=3)
    ax.annotate("", xy=(0, 10.3), xytext=(0, 9.8),
                 arrowprops=arrow_style, zorder=3)
    ax.annotate("", xy=(0, -10.3), xytext=(0, -9.8),
                 arrowprops=arrow_style, zorder=3)

    ax.set_xlabel("◀  Economic Left          Economic Right  ▶",
                  fontsize=12, fontweight="bold", color=_LABEL_COLOR, labelpad=10)
    ax.set_ylabel("▼  Libertarian          Authoritarian  ▼",
                  fontsize=12, fontweight="bold", color=_LABEL_COLOR, labelpad=10)

    ax.scatter(
        x, y,
        s=220,
        color=_POINT_COLOR,
        edgecolors=_POINT_EDGE,
        linewidths=2.5,
        zorder=5,
    )

    coord_text = f"({x:+.2f}, {y:+.2f})"
    ax.annotate(
        coord_text,
        xy=(x, y),
        xytext=(x + 0.4, y + 0.7),
        fontsize=10,
        fontweight="bold",
        color=_POINT_EDGE,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor=_POINT_EDGE,
            alpha=0.85,
        ),
        zorder=6,
    )

    legend_patches = [
        mpatches.Patch(color=_QUADRANT_COLORS["top_right"],    label="Right-Authoritarian"),
        mpatches.Patch(color=_QUADRANT_COLORS["top_left"],     label="Left-Authoritarian"),
        mpatches.Patch(color=_QUADRANT_COLORS["bottom_right"], label="Right-Libertarian"),
        mpatches.Patch(color=_QUADRANT_COLORS["bottom_left"],  label="Left-Libertarian"),
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.13),
        ncol=4,
        fontsize=9,
        framealpha=0.7,
        edgecolor="#cccccc",
    )

    ax.text(
        10, -9.5,
        "@Minerva_8value_bot",
        fontsize=9,
        ha="right",
        color="#666666",
        style="italic",
        alpha=0.7,
    )

    ax.set_title(
        "Political Compass",
        fontsize=18,
        fontweight="bold",
        color=_TITLE_COLOR,
        pad=16,
    )

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight",
                facecolor=_BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
