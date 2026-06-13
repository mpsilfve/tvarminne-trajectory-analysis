import click
import pandas as pd
from scipy.io import loadmat
from benedict import benedict

from tvarminne_trajectory_analysis.mat_io import load_mat, matlab_datenum_to_datetime

@click.command()
@click.option("--concentrations", help="Concentration data file", required=True)
@click.option("--trajectories", help="Trajectory data file", required=True)
def main(concentrations, trajectories):
    click.echo(f"Trajectory file: {trajectories}")
    click.echo(f"Concentration file: {concentrations}")

    concentrations_mat = load_mat(concentrations)
    trajectories_mat = load_mat(trajectories)

    print("\nConcentration key paths:")
    print(concentrations_mat.keypaths())

    dmps_data = concentrations_mat["dmpsData"]
    print("\ndmpsData:")
    print(f"  shape: {dmps_data.shape}")
    print(f"  dtype: {dmps_data.dtype}")
    print(f"  first row: {dmps_data[0, :]}")

    print("\nTrajectory key paths:")
    print(trajectories_mat.keypaths())

    latitudes = trajectories_mat["latitudes"]
    longitudes = trajectories_mat["longitudes"]
    time_datenum = trajectories_mat["time_datenum"]

    trajectory_times = matlab_datenum_to_datetime(time_datenum)

    print("\nTrajectories:")
    print(f"  latitudes shape:  {latitudes.shape}")
    print(f"  longitudes shape: {longitudes.shape}")
    print(f"  time shape:       {trajectory_times.shape}")
    print(f"  first time:       {trajectory_times[0]}")
    print(f"  last time:        {trajectory_times[-1]}")

    print("\nFirst trajectory:")
    print(f"  arrival lat/lon:  {latitudes[0, 0]}, {longitudes[0, 0]}")
    print(f"  final back point: {latitudes[0, -1]}, {longitudes[0, -1]}")

    print("\nMissing values:")
    print(f"  missing latitudes:  {pd.isna(latitudes).sum()}")
    print(f"  missing longitudes: {pd.isna(longitudes).sum()}")


if __name__ == "__main__":
    main()
