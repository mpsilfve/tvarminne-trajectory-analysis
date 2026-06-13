import numpy as np

from tvarminne_trajectory_analysis.consts import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, GRID_GRANULARITY

def make_lon_lat_grid(lat, lon, padding=1.0):
    """
    Create 1x1 degree grid edges and centers covering valid trajectory points.

    Returns
    -------
    lat_edges, lon_edges : arrays
        Grid cell boundaries.
    lat_centers, lon_centers : arrays
        Grid cell centers.
    """

    # Let's check that the majority of our data is included inside the
    # intended grid.
    inside = (
    ~np.isnan(lat)
    & ~np.isnan(lon)
    & (lat >= LAT_MIN)
    & (lat <= LAT_MAX)
    & (lon >= LON_MIN)
    & (lon <= LON_MAX)
    )
    
    valid = ~np.isnan(lat) & ~np.isnan(lon)

    print("\nTrajectory points inside domain:")
    print("  Overall valid trajectory points:", valid.sum())
    print("  Inside domain:", inside.sum())
    print("  Outside domain:", valid.sum() - inside.sum())
    print(f"  Fraction outside: {100 - 100*inside.sum() / valid.sum():.1f}%")

    lat_edges = np.arange(LAT_MIN, LAT_MAX + GRID_GRANULARITY, GRID_GRANULARITY)
    lon_edges = np.arange(LON_MIN, LON_MAX + GRID_GRANULARITY, GRID_GRANULARITY)

    lat_centers = lat_edges[:-1] + GRID_GRANULARITY / 2
    lon_centers = lon_edges[:-1] + GRID_GRANULARITY / 2

    return lat_edges, lon_edges, lat_centers, lon_centers

