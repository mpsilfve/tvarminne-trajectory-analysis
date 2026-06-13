import pandas as pd

from scipy.io import loadmat
from benedict import benedict

from tvarminne_trajectory_analysis.consts import MATLAB_DATENUM_UNIX_EPOCH

def load_mat(fn):
    return benedict(
        loadmat(
            fn,
            squeeze_me=True,
            struct_as_record=False,
            simplify_cells=True,
        )
    )

def matlab_datenum_to_datetime(values):
    return pd.to_datetime(values.ravel() - MATLAB_DATENUM_UNIX_EPOCH, unit="D")

def load_trajectories(fn):
    trajectories_mat = load_mat(fn)

    latitudes = trajectories_mat["latitudes"]
    longitudes = trajectories_mat["longitudes"]
    time_datenum = trajectories_mat["time_datenum"]
    trajectory_times = matlab_datenum_to_datetime(time_datenum)

    return latitudes, longitudes, trajectory_times
