import math
from matplotlib import figure
from matplotlib.axis import Axis
from matplotlib.collections import LineCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from typing import Any, List, Tuple


from src.const import (
    ABV_TO_RGB,
    IBU_TO_RGB,
    SRM_TO_HEX,
)
from src.data_models import BeerStyle


def make_color_chart(
    fig: figure.Figure, axs: Axis, sorted_vals: List[Any], color_list: List[str]
) -> Tuple[figure.Figure, Axis]:
    n = 1000

    for i in range(len(sorted_vals)):
        val = sorted_vals[i]
        x = np.linspace(val["xmin"], val["xmax"], n)
        y = [i + 1] * n
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        val_color_range = color_list[math.floor(val["xmin"]) : math.ceil(val["xmax"]) + 1]

        cmap = ListedColormap(val_color_range)
        norm = BoundaryNorm(list(range(math.floor(val["xmin"]), math.ceil(val["xmax"]) + 1)), cmap.N)
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(x)
        y_idx = i + 1
        axs.text(
            (val["xmin"] + val["xmax"]) / 2,
            y_idx,
            val["label"],
            color=val_color_range[0],
            ha="center",
            va="bottom",
            path_effects=[pe.withStroke(linewidth=0.15, foreground="black")],
        )
        axs.text(val["xmin"], y_idx, val["xmin"], color="black", ha="right", va="top", size="smaller")
        axs.text(val["xmax"], y_idx, val["xmax"], color="black", va="top", size="smaller")
        lc.set_linewidth(1)
        axs.add_collection(lc)
    return fig, axs


def make_chart(target_dir: str, chart_groups: List[BeerStyle], style_cat: str, metric_cat: str) -> None:
    vals = [
        {
            "label": style.name,
            "xmin": getattr(style, metric_cat).value_low,
            "xmax": getattr(style, metric_cat).value_high,
        }
        for style in chart_groups
        if getattr(style, metric_cat)
    ]
    global_xmin = min([x["xmin"] for x in vals])
    global_xmax = max([x["xmax"] for x in vals])
    sorted_vals = sorted(vals, key=lambda x: (x["xmin"], x["xmax"], x["label"]))
    title = f"{style_cat}: {metric_cat.title()}"
    fig, axs = plt.subplots()
    axs.set_xlim(max(global_xmin - 3, 0), global_xmax + 3)
    axs.set_ylim(0, len(sorted_vals) + 1)
    color_hex_list = SRM_TO_HEX
    if metric_cat == "bitterness":
        color_hex_list = IBU_TO_RGB
    elif metric_cat == "alcohol":
        color_hex_list = ABV_TO_RGB

    fig, axs = make_color_chart(fig, axs, sorted_vals, color_hex_list)
    plt.yticks([])
    axs.tick_params(axis="y", which="both", bottom=False, top=False, labelbottom=False)
    axs.set_title(title)
    fig.savefig(f"{target_dir}/{title}.png")
    plt.close(fig)
