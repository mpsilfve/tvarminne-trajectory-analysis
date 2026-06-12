import click
import numpy as np

from mat_io import load_trajectories
from consts import LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, GRID_GRANULARITY, STATION_LAT, STATION_LON
from grid import make_lon_lat_grid
from trajectories import remove_fully_missing_trajectories, count_trajectory_grid_visits, get_month_pooled_trajectories
from plot_map import plot_monthly_maps_same_scale

@click.command()
@click.option(
    "--trajectories",
    help="Clean trajectory .mat file",
    required=True
)
@click.option(
    "--outputfile",
    help="Output image file",
    required=True
)
def main(trajectories, outputfile):
    lat, lon, times = load_trajectories(trajectories)

    print("\nRaw trajectory arrays:")
    print("  lat:", lat.shape)
    print("  lon:", lon.shape)
    print("  times:", times.shape)
    orig_lats = lat.shape[0]

    lat, lon, times = remove_fully_missing_trajectories(lat, lon, times)

    print("\nAfter removing fully missing trajectories:")
    print("  lat:", lat.shape)
    print("  lon:", lon.shape)
    print("  times:", times.shape)
    print(f"  row loss: {100 - lat.shape[0]*100/orig_lats:.1f}%")

    lat_edges, lon_edges, lat_centers, lon_centers = make_lon_lat_grid(
        lat,
        lon
    )

    print("\nGrid:")
    print("  lat edges:", lat_edges[0], "to", lat_edges[-1])
    print("  lon edges:", lon_edges[0], "to", lon_edges[-1])
    print("  number of lat cells:", len(lat_centers))
    print("  number of lon cells:", len(lon_centers))
    print("  grid shape:", (len(lat_centers), len(lon_centers)))

    print("\nExample:")
    print("  first lat centers:", lat_centers[:5])
    print("  first lon centers:", lon_centers[:5])

    monthly_pooled_trajectories = get_month_pooled_trajectories(lat, lon, times,
                                                                lat_edges, lon_edges,
                                                                range(1,13),
                                                                exclude_station=False)

    pooled_trajectories = count_trajectory_grid_visits(
            lat,
            lon,
            lat_edges,
            lon_edges,
            exclude_station=False
        )

    monthly_pooled_trajectories = {month:grid - pooled_trajectories/12 for month, grid in monthly_pooled_trajectories.items()}
    plot_monthly_maps_same_scale(monthly_pooled_trajectories,
                                 lat_edges,
                                 lon_edges,
                                 outputfile,
                                 "Monthly trajectory anomaly maps")

if __name__ == "__main__":
    main()
