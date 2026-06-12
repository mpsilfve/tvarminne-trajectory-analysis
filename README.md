# Hanko station trajectory analysis

This repository contains an exploratory trajectory-analysis pipeline for back trajectories arriving at the Hanko measurement station. The goal is to implement [PSCF (Potential Source Contribution Function) and the concentration-field (CF) approaches](https://acp.copernicus.org/articles/13/2153/2013/acp-13-2153-2013.pdf) together with other useful plots of the Hanko station measurement data.

## How to set up the project?

### 1. Set up virtual environment:
```
% python3 -m venv venv
% source venv/bin/activate
```

### 2. Install requirements:
```
pip3 install -r requirements.txt
```

### 3. Retrieve data 

Raw data files are not committed to this repository due to size. Get [data](https://drive.google.com/file/d/1PUnODhPx2qdvTnDETKcWLZU494rbMX1f/view?usp=sharing) from Google Drive (may require access in which case contact Miikka Silfverberg). Unpack to produce a directory `data`:

```
% gdown "https://drive.google.com/file/d/1PUnODhPx2qdvTnDETKcWLZU494rbMX1f/view?usp=sharing"
% tar -xzvf hanko_data.tgz
```

## How to generate plots?

### Overall monthly trajectory anomalies

This script illustrates monthly trajectory anomalies per grid cell. Positive values (yellower) indicate cells visited more often than the annual monthly mean for that cell; negative values (bluer) indicate cells visited less often. 

```
python3 scripts/plot_monthly_trajectory_anomalies.py --trajectories data/trajectorydata_clean.mat --outputfile plots/monthly_trajectory_anomalies.png
```

![Plot](plots/monthly_trajectory_anomalies.png)
