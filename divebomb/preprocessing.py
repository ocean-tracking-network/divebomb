import math

import numpy as np
import pandas as pd
import xarray as xr
from netCDF4 import Dataset, date2num, num2date


def zlib_encoding(ds):
    """
    This is a helper function for xarray to compress all variables going to
    netCDF

    :param ds: an xarray Dataset

    :return: A dictionary indicating zlib compression for all variables
    """
    comp = dict(zlib=True)
    encoding = {var: comp for var in ds.data_vars}
    return encoding


def calculate_window_mean(window, surface_threshold, df):
    """

    :param window: an int to determine the size for a rolling median
    :param surface_threshold: the maximum depth that will be considered for the
        offset
    :param df: Pandas Dataframe of the dive data

    :return: An average offset in meters using the defined window
    """
    data = df.copy(deep=True)
    data['adjusted_depth'] = data[
        data.depth <= surface_threshold].depth.rolling(window).median()
    data.adjusted_depth = data.adjusted_depth.interpolate()
    data.adjusted_depth = data.depth - data.adjusted_depth
    avg_adjustment = (data.depth - data.adjusted_depth).mean()
    del data
    return avg_adjustment


def correct_depth_offset(data,
                         window=3600,
                         columns={
                             'depth': 'depth',
                             'time': 'time'
                         },
                         aux_file='corrected_depth_auxillary_data.nc',
                         method='max',
                         surface_threshold=4):
    """
    :param data: The dataset consisting of a time and a depth column
    :param window: time window (in seconds) to use in the calculation
    :param aux_file: A netCDF file to write all of the calculated offsets and
        window size
    :param columns: column renaming dictionary if needed
    :param method: either 'max' or 'mean' declaring the calculation method,
        default is max
    :param surface_threshold: maximum values (in meters) to use when using the
        mean the calculate

    :return: A DataFrame with a corrected depth
    """

    if method == 'mean':
        window_means = pd.DataFrame(
            np.arange(10, 1001, step=10), columns=['window_size'])
        window_means['offset_mean'] = window_means.window_size.apply(
            calculate_window_mean, args=(surface_threshold, data))
        window = window_means.iloc[(
            (window_means.offset_mean.diff() / window_means.window_size).diff(
            ) / window_means.window_size).idxmin()].window_size.astype(int)

        data['depth_offset'] = data[data.depth < animal_length].depth.rolling(
            window).median()
        data.depth_offset = data.depth_offset.interpolate().fillna(0)
        data['corrected_depth'] = data.depth - data.depth_offset
    else:
        data['offset'] = data.depth.rolling(
            int(window / data.time.diff().mean().total_seconds())).min()
        data.offset.fillna(data.offset.min(), inplace=True)
        data['corrected_depth'] = data.depth - data.offset

    data['window_size_in_seconds'] = window
    corrected_data = pd.DataFrame()
    corrected_data['time'] = data.time
    corrected_data['depth'] = data.corrected_depth

    time_units = 'seconds since 1970-01-01'
    data.time = date2num(pd.to_datetime(data.time).tolist(), units=time_units)
    xarray_data = xr.Dataset(data)
    xarray_data.variables['time'].attrs = {'units': time_units}
    xarray_data.variables['depth'].attrs = {
        'units': 'meters',
        'positive': 'down'
    }
    xarray_data.variables['corrected_depth'].attrs = {
        'units': 'meters',
        'positive': 'down'
    }
    xarray_data.to_netcdf(
        aux_file, mode='w', encoding=zlib_encoding(xarray_data))
    xarray_data.close()

    return corrected_data
