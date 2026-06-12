import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def labels_to_edges(labels):
    labels = np.asarray(labels)
    step = labels[1] - labels[0]
    return np.concatenate([
        [labels[0] - step / 2],
        labels[:-1] + step / 2,
        [labels[-1] + step / 2],
    ])

def plot_grid_on_map(
    grid,
    lat_labels,
    lon_labels,
    title,
    output_path=None,
    station_lat=None,
    station_lon=None):
    lat_edges = labels_to_edges(lat_labels)
    lon_edges = labels_to_edges(lon_labels)

    # Mask zero-count cells so empty areas are transparent/blank
    plot_grid = grid.astype(float)
    plot_grid[plot_grid == 0] = np.nan

    fig = plt.figure(figsize=(8, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.set_extent(
        [lon_edges.min(), lon_edges.max(), lat_edges.min(), lat_edges.max()],
        crs=ccrs.PlateCarree(),
    )

    mesh = ax.pcolormesh(
        lon_edges,
        lat_edges,
        plot_grid,
        transform=ccrs.PlateCarree(),
        shading="auto",
    )

    ax.coastlines(resolution="50m", linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.LAND, alpha=0.2)
    ax.add_feature(cfeature.OCEAN, alpha=0.1)

    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.3,
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False

    if station_lat is not None and station_lon is not None:
        ax.scatter(
            station_lon,
            station_lat,
            marker="*",
            s=80,
            transform=ccrs.PlateCarree(),
            label="Station",
        )
        ax.legend(loc="lower left")

    cbar = plt.colorbar(mesh, ax=ax, shrink=0.75)
    cbar.set_label("Trajectory count")

    ax.set_title(title)

    if output_path is not None:
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
