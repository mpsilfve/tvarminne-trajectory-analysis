# Plots

### PSCF plots for high particle concentration events

The following command generates monthly PSCF maps for a selected DMPS particle-size bin. High-concentration trajectories are defined using the chosen percentile threshold (--highperc), and each grid cell is assigned the fraction of trajectories passing through that cell that were associated with high particle concentration at Tvärminne. These plots are preliminary PSCF diagnostics and should be interpreted as air-mass pathway associations, not direct source-attribution maps.

```
python3 scripts/plot_pscf.py --concentrations data/dmpsdata.mat --trajectories data/trajectorydata_clean.mat --particlesize 25 --highperc 0.75 --outputfile plots/monthly_pscf_anomalies.png
```

![Plot](monthly_pscf_anomalies.png)

### Overall monthly trajectory anomalies

This script illustrates monthly trajectory anomalies per grid cell. Positive values (yellower) indicate cells visited more often than the annual monthly mean for that cell; negative values (bluer) indicate cells visited less often. **Note that these plots do not show any particle concentrations**, only trajectory data.

```
python3 scripts/plot_monthly_trajectory_anomalies.py --trajectories data/trajectorydata_clean.mat --outputfile plots/monthly_trajectory_anomalies.png
```

![Plot](monthly_trajectory_anomalies.png)

