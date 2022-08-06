import os

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt

from scrape.core import Session

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_fastest_lap_gear_plot(
    session: Session, year: int, circuit_id: str, driver_number: str, driver_id: str
):
    directory = os.path.join(ROOT_DIR, "..", "public", "gear-plots", str(year), circuit_id)
    filename = os.path.join(directory, f"{driver_id}.svg")

    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(filename):
        return

    lap = session.laps.pick_driver(driver_number).pick_fastest()
    tel = lap.get_telemetry()

    color = "#F1E9DA"

    fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.5), dpi=200)
    ax.axis("off")

    ax.plot(
        lap.telemetry["X"], lap.telemetry["Y"], color=color, linestyle="-", linewidth=19, zorder=0
    )

    x = np.array(tel["X"].values)
    y = np.array(tel["Y"].values)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    gear = tel["nGear"].to_numpy().astype(float)

    # prepare colors
    cmap = mpl.cm.get_cmap("tab10")
    cm_norm = plt.Normalize(0, 10)

    lc_comp = mpl.collections.LineCollection(
        segments, norm=cm_norm, cmap=cmap, linestyle="-", linewidth=16
    )
    lc_comp.set_array(gear)

    gca = fig.gca()
    gca.add_collection(lc_comp)
    ax.axis("equal")
    ax.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    plt.rcParams["ytick.color"] = color
    cbar = fig.colorbar(mappable=lc_comp, boundaries=np.arange(1, 10))
    cbar.set_ticks(np.arange(1.5, 9.5))
    cbar.set_ticklabels(np.arange(1, 9), color=color, fontsize=16)
    cbar.outline.set_color(color)
    plt.savefig(filename, transparent=True, bbox_inches="tight")
