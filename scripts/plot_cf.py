import click
import numpy as np
import pandas as pd

from tvarminne_trajectory_analysis.mat_io import load_mat, matlab_datenum_to_datetime
from tvarminne_trajectory_analysis.grid import make_lon_lat_grid
from tvarminne_trajectory_analysis.trajectories import remove_fully_missing_trajectories, count_trajectory_grid_visits, get_month_weighted_trajectories, get_month_pooled_trajectories
from tvarminne_trajectory_analysis.concentrations import remove_missing_concentrations, find_concentrations
from tvarminne_trajectory_analysis.plot_map import plot_monthly_maps_same_scale

@click.command()
@click.option("--concentrations", help="Concentration data file", required=True)
@click.option("--trajectories", help="Trajectory data file", required=True)
@click.option("--particlesize", help="Particle size index in {13, ..., 36} in concentration data file (Matlab indexing starts at 1)", required=True)
@click.option("--outputfile", help="Output image file", required=True)
@click.option("--minimumtrajectorycount", help="Cells need to occur in minimally this many trajectories", required=True)
def main(concentrations, trajectories, particlesize, outputfile, minimumtrajectorycount):
    click.echo(f"Trajectory file: {trajectories}")
    click.echo(f"Concentration file: {concentrations}")
    click.echo(f"Particle size index: {particlesize}")
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
    concentrations = concentrations[concentrations[:,-1] > 0]
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

    # Find nearest neighbor concentration time-stamps (actually this
    # might give slightly different results because this is the
    # nearest preceding time stamp)
    nearest_concentrations = find_concentrations(time, concentrations)
    print("Concentrations")
    print(nearest_concentrations)
    time = pd.to_datetime(time).round("s")
    
    lat = lat[(time >= nearest_concentrations["trajectory_time"].min()) &
              (time <= nearest_concentrations["trajectory_time"].max())]
    lon = lon[(time >= nearest_concentrations["trajectory_time"].min()) &
              (time <= nearest_concentrations["trajectory_time"].max())]
    time = time[(time >= nearest_concentrations["trajectory_time"].min()) &
                (time <= nearest_concentrations["trajectory_time"].max())]
    
    monthly_weighted_trajectories = get_month_weighted_trajectories(lat, lon, time, nearest_concentrations["concentration"],
                                                                  lat_edges, lon_edges,
                                                                  range(1,13),
                                                                  exclude_station=False)

    # Geometric mean of concentrations
    print(nearest_concentrations["concentration"].min())
    print(np.log(nearest_concentrations["concentration"]).mean())
    mean_concentration = np.exp(np.log(nearest_concentrations["concentration"]).mean())
    
    print(mean_concentration)
    anomaly = {month:(monthly_weighted_trajectories[month]/monthly_pooled_trajectories[month] - mean_concentration)/mean_concentration
                          for month in monthly_pooled_trajectories}
    plot_monthly_maps_same_scale(anomaly,
                                 lat_edges,
                                 lon_edges,
                                 outputfile,
                                 f"Concentration anomaly for particle size {particle_size_nm} nm (method: CF)",
                                 colorbar_label="CF",
                                 kind="anomaly",
                                 cmap="turbo",
                                 alpha=0.75,
                                 vmin=-1,
                                 vmax=1)

if __name__=="__main__":
    main()
