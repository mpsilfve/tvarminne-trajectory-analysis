"""Map plotting utilities for Hanko trajectory-grid analysis.

The functions here assume that the gridded data are already computed on a
latitude-label x longitude-label grid, for example

    lat_labels = np.arange(50, 76)  # 50, 51, ..., 75
    lon_labels = np.arange(0, 46)   # 0, 1, ..., 45

where each label is the centre of a rounded 1° x 1° grid cell. The plotting
functions convert these labels into cell edges by shifting by half a grid step.

Input grids should have shape

    (len(lat_labels), len(lon_labels))

with latitude as axis 0 and longitude as axis 1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize, TwoSlopeNorm

import cartopy.crs as ccrs
import cartopy.feature as cfeature


MONTH_NAMES_SHORT = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def labels_to_edges(labels: np.ndarray) -> np.ndarray:
    """Convert regularly spaced grid-centre labels to cell-edge coordinates.

    Example
    -------
    [50, 51, 52] -> [49.5, 50.5, 51.5, 52.5]
    """
    labels = np.asarray(labels, dtype=float)

    if labels.ndim != 1:
        raise ValueError("labels must be a one-dimensional array")
    if labels.size < 2:
        raise ValueError("at least two labels are needed to infer grid spacing")

    steps = np.diff(labels)
    if not np.allclose(steps, steps[0]):
        raise ValueError("labels must be regularly spaced")

    step = steps[0]
    return np.concatenate(
        [
            [labels[0] - step / 2],
            labels[:-1] + step / 2,
            [labels[-1] + step / 2],
        ]
    )


def make_hanko_lambert_crs(
    central_longitude: float = 22.5,
    central_latitude: float = 62.5,
    standard_parallels: tuple[float, float] = (55.0, 70.0),
) -> ccrs.LambertConformal:
    """Return a Lambert conformal conic projection for the Hanko domain.

    The trajectory grid itself is still lon/lat data. This projection only
    controls how the map is drawn.
    """
    return ccrs.LambertConformal(
        central_longitude=central_longitude,
        central_latitude=central_latitude,
        standard_parallels=standard_parallels,
    )


def _prepare_grid_for_plotting(
    grid: np.ndarray,
    mask_zeros: bool,
) -> np.ndarray:
    """Return a float grid suitable for pcolormesh."""
    plot_grid = np.asarray(grid, dtype=float).copy()

    if plot_grid.ndim != 2:
        raise ValueError("grid must be two-dimensional")

    if mask_zeros:
        plot_grid[plot_grid == 0] = np.nan

    return plot_grid


def _add_base_map(
    ax,
    lon_edges: np.ndarray,
    lat_edges: np.ndarray,
    show_gridlines: bool = True,
):
    """Add coastlines, borders, and optional gridline labels."""
    ax.set_extent(
        [lon_edges.min(), lon_edges.max(), lat_edges.min(), lat_edges.max()],
        crs=ccrs.PlateCarree(),
    )

    ax.coastlines(resolution="50m", linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)
    ax.add_feature(cfeature.LAND, alpha=0.15)
    ax.add_feature(cfeature.OCEAN, alpha=0.08)

    if show_gridlines:
        gl = ax.gridlines(
            draw_labels=True,
            linewidth=0.25,
            alpha=0.5,
            linestyle="--",
        )
        gl.top_labels = False
        gl.right_labels = False
        return gl

    return None


def plot_grid_on_map(
    grid: np.ndarray,
    lat_labels: np.ndarray,
    lon_labels: np.ndarray,
    title: str,
    output_path: str | Path | None = None,
    station_lat: float | None = None,
    station_lon: float | None = None,
    projection=None,
    norm=None,
    vmin: float | None = None,
    vmax: float | None = None,
    cmap=None,
    colorbar_label: str = "Value",
    mask_zeros: bool = False,
    show: bool = False,
):
    """Plot one latitude-longitude grid on a projected map.

    Parameters
    ----------
    grid:
        2D array with shape (len(lat_labels), len(lon_labels)).
    lat_labels, lon_labels:
        Grid-centre labels, usually integer degree labels.
    title:
        Figure title.
    output_path:
        If given, save the figure to this path.
    station_lat, station_lon:
        Optional station marker position.
    projection:
        Cartopy projection used for drawing the map. Defaults to Lambert
        conformal conic for the Hanko/Baltic domain.
    norm, vmin, vmax:
        Matplotlib normalization/color-scale controls. Pass either `norm` or
        `vmin`/`vmax`, not both.
    cmap:
        Optional Matplotlib colormap name/object. Leave as None to use the
        Matplotlib default.
    colorbar_label:
        Label for the colorbar.
    mask_zeros:
        If True, zero-valued cells are plotted as empty/transparent.
    show:
        If True, display interactively. If False and output_path is given,
        close the figure after saving.
    """
    if norm is not None and (vmin is not None or vmax is not None):
        raise ValueError("pass either norm or vmin/vmax, not both")

    if projection is None:
        projection = make_hanko_lambert_crs()

    lat_edges = labels_to_edges(lat_labels)
    lon_edges = labels_to_edges(lon_labels)
    plot_grid = _prepare_grid_for_plotting(grid, mask_zeros=mask_zeros)

    fig, ax = plt.subplots(
        figsize=(8, 7),
        subplot_kw={"projection": projection},
    )

    mesh = ax.pcolormesh(
        lon_edges,
        lat_edges,
        plot_grid,
        transform=ccrs.PlateCarree(),
        shading="auto",
        norm=norm,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
    )

    _add_base_map(ax, lon_edges=lon_edges, lat_edges=lat_edges)

    if station_lat is not None and station_lon is not None:
        ax.scatter(
            station_lon,
            station_lat,
            marker="*",
            s=80,
            transform=ccrs.PlateCarree(),
            label="Station",
            zorder=5,
        )
        ax.legend(loc="lower left")

    cbar = fig.colorbar(mesh, ax=ax, shrink=0.75)
    cbar.set_label(colorbar_label)

    ax.set_title(title)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax


def plot_monthly_maps_same_scale(
    monthly_grids: Mapping[int, np.ndarray],
    lat_labels: np.ndarray,
    lon_labels: np.ndarray,
    output_path: str | Path | None = None,
    title: str = "Monthly trajectory maps",
    colorbar_label: str = "Value",
    kind: str = "anomaly",
    station_lat: float | None = None,
    station_lon: float | None = None,
    projection=None,
    cmap=None,
    mask_zeros: bool = False,
    show: bool = False,
    alpha: float = 1
):
    """Plot all 12 monthly grids in one 4 x 3 figure using one color scale.

    Parameters
    ----------
    monthly_grids:
        Mapping from month number 1..12 to a 2D grid.
    kind:
        "anomaly" for signed difference maps centred at zero, or "count" for
        non-negative count/intensity maps using vmin=0.
    """
    missing_months = sorted(set(range(1, 13)) - set(monthly_grids.keys()))
    if missing_months:
        raise ValueError(f"monthly_grids is missing months: {missing_months}")

    if projection is None:
        projection = make_hanko_lambert_crs()

    lat_edges = labels_to_edges(lat_labels)
    lon_edges = labels_to_edges(lon_labels)

    grids = {
        month: _prepare_grid_for_plotting(grid, mask_zeros=mask_zeros)
        for month, grid in monthly_grids.items()
    }

    if kind == "anomaly":
        lim = max(np.nanmax(np.abs(grid)) for grid in grids.values())
        norm = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
        vmin = None
        vmax = None
    elif kind == "count":
        norm = None
        vmin = 0.0
        vmax = max(np.nanmax(grid) for grid in grids.values())
    else:
        raise ValueError("kind must be either 'anomaly' or 'count'")

    fig, axes = plt.subplots(
        4,
        3,
        figsize=(12, 14),
        subplot_kw={"projection": projection},
        constrained_layout=True,
    )

    mesh = None

    for ax, month in zip(axes.ravel(), range(1, 13)):
        grid = grids[month]

        mesh = ax.pcolormesh(
            lon_edges,
            lat_edges,
            grid,
            transform=ccrs.PlateCarree(),
            shading="auto",
            norm=norm,
            vmin=vmin,
            vmax=vmax,
            cmap=cmap,
            alpha=alpha
        )

        _add_base_map(ax, lon_edges=lon_edges, lat_edges=lat_edges)
        ax.set_title(MONTH_NAMES_SHORT[month])

        if station_lat is not None and station_lon is not None:
            ax.scatter(
                station_lon,
                station_lat,
                marker="*",
                s=45,
                transform=ccrs.PlateCarree(),
                zorder=5,
            )

    fig.suptitle(title, fontsize=16)

    cbar = fig.colorbar(
        mesh,
        ax=axes.ravel().tolist(),
        shrink=0.75,
        orientation="vertical",
        alpha=alpha
    )
    cbar.set_label(colorbar_label)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=200, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

    return fig, axes


if __name__ == "__main__":
    # Minimal smoke test with random data. Run with:
    # python plot_map.py
    lat_labels = np.arange(50, 76, dtype=int)
    lon_labels = np.arange(0, 46, dtype=int)

    rng = np.random.default_rng(0)
    monthly = {
        month: rng.normal(size=(len(lat_labels), len(lon_labels)))
        for month in range(1, 13)
    }

    plot_monthly_maps_same_scale(
        monthly,
        lat_labels,
        lon_labels,
        output_path="outputs/figures/smoke_test_monthly_anomalies.png",
        title="Smoke test monthly anomalies",
        colorbar_label="Anomaly",
        kind="anomaly",
        station_lat=59.84,
        station_lon=23.25,
    )
