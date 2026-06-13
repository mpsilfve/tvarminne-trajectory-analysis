import numpy as np

from tvarminne_trajectory_analysis.mat_io import load_trajectories
from tvarminne_trajectory_analysis.consts import STATION_LAT, STATION_LON

lat, lon, _ = load_trajectories("data/trajectorydata_clean.mat")

print("First trajectory point:")
print("lat[0, 0] =", lat[0, 0])
print("lon[0, 0] =", lon[0, 0])

print("First-column ranges:")
print("lat[:, 0] min/max:", np.nanmin(lat[:, 0]), np.nanmax(lat[:, 0]))
print("lon[:, 0] min/max:", np.nanmin(lon[:, 0]), np.nanmax(lon[:, 0]))

dist_first = np.sqrt((lat[:, 0] - STATION_LAT)**2 + (lon[:, 0] - STATION_LON)**2)
dist_last = np.sqrt((lat[:, -1] - STATION_LAT)**2 + (lon[:, -1] - STATION_LON)**2)

print("First column:")
print("  median distance:", np.nanmedian(dist_first))
print("  mean distance:  ", np.nanmean(dist_first))
print("  min/max:        ", np.nanmin(dist_first), np.nanmax(dist_first))

print("Last column:")
print("  median distance:", np.nanmedian(dist_last))
print("  mean distance:  ", np.nanmean(dist_last))
print("  min/max:        ", np.nanmin(dist_last), np.nanmax(dist_last))

if np.nanmedian(dist_first) < np.nanmedian(dist_last):
    print("Likely order: Hanko -> remote, i.e. first column is arrival/station.")
else:
    print("Likely order: remote -> Hanko, i.e. last column is arrival/station.")
