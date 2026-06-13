import click
import numpy as np

from tvarminne_trajectory_analysis.consts import STATION_LAT, STATION_LON

def remove_fully_missing_trajectories(lat, lon, times):
    """
    Remove rows where the whole trajectory is missing.
    """
    valid_rows = ~(np.isnan(lat).all(axis=1) | np.isnan(lon).all(axis=1))

    return lat[valid_rows], lon[valid_rows], times[valid_rows]

def count_trajectory_grid_visits(masked_lat, masked_lon, lat_labels, lon_labels, exclude_station):
    """Count binary trajectory visits to rounded 1° x 1° grid cells.

    Each trajectory contributes at most one count to each visited cell.
    This matches the MATLAB-style unique([lat, lon], 'rows') logic.

    We loop here because it's easier when we want to retain unique
    visits per trajectory.

    If exclude_station==True, we filter our counts for the measuring
    station cell. This can lead to improved color resolution in
    certain plots because the station cell is visited by every single
    trajectory. Note that this is usually not needed when plotting
    deviation from average.

    """
    count_grid = np.zeros((lat_labels.shape[0], lon_labels.shape[0]), dtype=int)

    lat_min = lat_labels.min()
    lat_max = lat_labels.max()
    lon_min = lon_labels.min()
    lon_max = lon_labels.max()

    for lat_row, lon_row in zip(masked_lat, masked_lon):
        valid = ~np.isnan(lat_row) & ~np.isnan(lon_row)

        lat_cell = np.rint(lat_row[valid]).astype(int)
        lon_cell = np.rint(lon_row[valid]).astype(int)

        inside = (
            (lat_cell >= lat_min)
            & (lat_cell <= lat_max)
            & (lon_cell >= lon_min)
            & (lon_cell <= lon_max)
        )

        filter_station = ((lat_cell != round(STATION_LAT)) |
                          (lon_cell != round(STATION_LON))) if exclude_station else True
        
        lat_idx = (lat_cell[inside & filter_station] - lat_min).astype(int)
        lon_idx = (lon_cell[inside & filter_station] - lon_min).astype(int)

        if len(lat_idx) == 0:
            continue

        # One visit per trajectory per cell
        pairs = np.column_stack([lat_idx, lon_idx])
        pairs = np.unique(pairs, axis=0)

        np.add.at(count_grid, (pairs[:, 0], pairs[:, 1]), 1)

    return count_grid

def get_month_pooled_trajectories(lat, lon, times, lat_edges, lon_edges, month, exclude_station=False):
    monthly_counts = {}
    for month in range(1, 13):
        time_mask = times.month == month
        monthly_counts[month] = count_trajectory_grid_visits(
            lat[time_mask],
            lon[time_mask],
            lat_edges,
            lon_edges,
            exclude_station
        )
    return monthly_counts
