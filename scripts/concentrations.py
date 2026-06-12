import click
import numpy as np
import pandas as pd

from consts import MATLAB_DATENUM_UNIX_EPOCH

def remove_missing_concentrations(concentrations):
    """
    Remove rows where the concentration is missing.
    """
    valid_rows = ~np.isnan(concentrations[:,-1])

    return concentrations[valid_rows]

def find_high_concentrations(trajectory_times, concentrations, threshold):
    traj_df = pd.DataFrame({
        "trajectory_time": pd.to_datetime(trajectory_times),
        "trajectory_id": np.arange(len(trajectory_times)),
    })

    time_cols = concentrations[:, :6]
    conc_times = pd.to_datetime({
        "year": time_cols[:, 0].astype(int),
        "month": time_cols[:, 1].astype(int),
        "day": time_cols[:, 2].astype(int),
        "hour": time_cols[:, 3].astype(int),
        "minute": time_cols[:, 4].astype(int),
        "second": time_cols[:, 5].astype(int),
    })

    conc_df = pd.DataFrame({
        "concentration_time": pd.to_datetime(conc_times),
        "concentration": concentrations[:,-1],
    })

    traj_df = traj_df.sort_values("trajectory_time")
    conc_df = conc_df.sort_values("concentration_time")

    conc_df["is_high"] = conc_df["concentration"] >= threshold

    matched = pd.merge_asof(
        traj_df,
        conc_df,
        left_on="trajectory_time",
        right_on="concentration_time",
        direction="backward",
    )

    matched = matched[matched["is_high"].notna()]
    high_times = matched[matched["is_high"]]["trajectory_time"]
    return pd.to_datetime(high_times).dt.round("s")

