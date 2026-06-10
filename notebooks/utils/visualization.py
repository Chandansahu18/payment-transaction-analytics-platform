import logging

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from notebooks.utils.config import CHARTS_DIR

logger = logging.getLogger(__name__)

NOTEBOOK_DPI = 100
SAVE_DPI = 150


def save_chart(
    fig: Figure,
    filename: str,
    subdir: str = "",
    show: bool = True,
) -> None:
    """Save chart to notebooks/charts/ and show native matplotlib output in Jupyter."""
    target_dir = CHARTS_DIR / subdir if subdir else CHARTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = filename.removesuffix(".png")
    out_path = target_dir / f"{stem}.png"
    fig.savefig(out_path, dpi=SAVE_DPI, bbox_inches="tight", facecolor="white", pad_inches=0.25)
    logger.info("Saved chart → notebooks/charts/%s%s", f"{subdir}/" if subdir else "", out_path.name)

    if show:
        try:
            from IPython.core.getipython import get_ipython
            from IPython.display import display

            ip = get_ipython()
            if ip is not None:
                display(fig)
        except ImportError:
            pass

    plt.close(fig)


def new_fig(width: float = 10, height: float = 4) -> tuple[Figure, Axes]:
    """Standard single-panel figure with room for title + labels."""
    fig, ax = plt.subplots(figsize=(width, height), dpi=NOTEBOOK_DPI, layout="constrained")
    return fig, ax


def minimal_heatmap(
    data: pd.DataFrame,
    ax: Axes,
    *,
    cmap: str = "Blues",
    cbar_label: str = "",
    vmin: float | None = None,
    vmax: float | None = None,
) -> None:
    """Clean heatmap — no cell annotations, axis labels + colorbar only."""
    sns.heatmap(
        data,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=False,
        cbar_kws={"label": cbar_label, "shrink": 0.85},
        linewidths=0.4,
        linecolor="white",
    )