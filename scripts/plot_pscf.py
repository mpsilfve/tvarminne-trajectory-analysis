import click
import numpy as np
import pandas as pd

from tvarminne_trajectory_analysis.mat_io import load_mat, matlab_datenum_to_datetime
from tvarminne_trajectory_analysis.grid import make_lon_lat_grid
from tvarminne_trajectory_analysis.trajectories import remove_fully_missing_trajectories, count_trajectory_grid_visits, get_month_pooled_trajectories
from tvarminne_trajectory_analysis.concentrations import remove_missing_concentrations, find_high_concentrations
from tvarminne_trajectory_analysis.plot_map import plot_monthly_maps_same_scale

@click.command()
@click.option("--concentrations", help="Concentration data file", required=True)
@click.option("--trajectories", help="Trajectory data file", required=True)
@click.option("--particlesize", help="Particle size index in {13, ..., 36} in concentration data file (Matlab indexing starts at 1)", required=True)
@click.option("--highperc", help="High concentration percentile, e.g. 0.9 for the 90th percentile.", required=True)
@click.option("--outputfile", help="Output image file", required=True)
@click.option("--minimumtrajectorycount", help="Cells need to occur in minimally this many trajectories", required=True)
def main(concentrations, trajectories, particlesize, highperc, outputfile, minimumtrajectorycount):
    click.echo(f"Trajectory file: {trajectories}")
    click.echo(f"Concentration file: {concentrations}")
    click.echo(f"Particle size index: {particlesize}")
    click.echo(f"High concentration percentile: {highperc}")
    click.echo(f"Output file: {outputfile}")
    click.echo(f"Minimum trajectory count: {minimumtrajectorycount}")
    
    # Read trajectories and create grid
    trajectories_mat = load_mat(trajectories)
    lat = trajectories_mat["latitudes"]
    lon = trajectories_mat["longitudes"]
    time = matlab_datenum_to_datetime(trajectories_mat["time_datenum"])
    lat, lon, time = remove_fully_missing_trajectories(lat, lon, time) 
    lat_edges, lon_edges, lat_centers, lon_centers = make_lon_lat_grid(lat, lon)

    minimumtrajectorycount=int(minimumtrajectorycount)
    monthly_pooled_trajectories = get_month_pooled_trajectories(lat, lon, time,
                                                                lat_edges, lon_edges,
                                                                range(1,13),
                                                                exclude_station=False,
                                                                min_traj_count=minimumtrajectorycount)
    

    # Read concentrations and filter out
    particlesize = int(particlesize)
    concentrations_mat = load_mat(concentrations)['dmpsData']
    concentrations = concentrations_mat[:, [0, 1, 2, 3, 4, 5, particlesize - 1]]

    # The start of the file (first 58 rows) has zero counts (maybe
    # station wasn't active?). Remove those.
    concentrations = concentrations[58:]
    particle_size_nm = concentrations[0,-1]
    print(f"\nParticle size {particlesize} corresponds to {particle_size_nm:.1f} nm")

    # Only every other row contains actual
    # concentrations. Additionally, some entries are NaN.
    concentrations = concentrations[1::2]
    concentrations = remove_missing_concentrations(concentrations)
    print("\nFirst 5 concentration rows. Check that counts are non-zero:")
    print(concentrations[:5,:])
    print("\nFinal 5 concentration rows. Check that counts are non-zero:")
    print(concentrations[-5:,:])
    
    print(f"\nNumber of concentration entries: {concentrations.shape[0]}")

    # Compute percentile
    highperc = float(highperc)
    threshold = np.nanquantile(concentrations[:-1], highperc)

    # Find trajectory time stamps corresponding to high_concentrations
    high_times = find_high_concentrations(time, concentrations, threshold)

    trajectory_times = pd.Series(pd.to_datetime(time)).dt.round("s")
    high_times = pd.Series(pd.to_datetime(high_times)).dt.round("s")
    
    high_set_set = set(high_times)
    trajectory_is_high = trajectory_times.isin(high_set_set).to_numpy()
    lat_high = lat[trajectory_is_high]
    lon_high = lon[trajectory_is_high]
    high_times = time[trajectory_is_high]
    
    monthly_high_pooled_trajectories = get_month_pooled_trajectories(lat_high, lon_high, high_times,
                                                                     lat_edges, lon_edges,
                                                                     range(1,13),
                                                                     exclude_station=False)

    anomaly = {month:monthly_high_pooled_trajectories[month]/monthly_pooled_trajectories[month]
               for month in monthly_pooled_trajectories}
    plot_monthly_maps_same_scale(anomaly,
                                 lat_edges,
                                 lon_edges,
                                 outputfile,
                                 f"Concentration anomaly (> {100*highperc}th percentile) for particle size {particle_size_nm} nm (method: PSCF)",
                                 colorbar_label="PSCF",
                                 kind="count",
                                 cmap="turbo",
                                 alpha=0.75)

if __name__=="__main__":
    main()
