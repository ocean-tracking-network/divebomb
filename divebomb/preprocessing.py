from netCDF4 import Dataset, num2date, date2num
import math
import pandas as pd
import numpy as np
import xarray as xr


def zlib_encoding(ds):
    comp = dict(zlib=True)
    encoding = {var: comp for var in ds.data_vars}
    return encoding

def calculate_window_mean(window, surface_threshold, df):
    data = df.copy(deep=True)
    data['adjusted_depth'] = data[data.depth <= surface_threshold].depth.rolling(window).median()
    data.adjusted_depth = data.adjusted_depth.interpolate()
    data.adjusted_depth = data.depth - data.adjusted_depth
    avg_adjustment = (data.depth - data.adjusted_depth).mean()
    del data
    return avg_adjustment

def correct_depth_offset(data, animal_length, aux_file='corrected_depth_auxillary_data.nc'):
    surface_threshold = math.cos(math.radians(45)) * animal_length
    window_means = pd.DataFrame(np.arange(10,1001, step=10), columns=['window_size'])
    window_means['offset_mean'] = window_means.window_size.apply(calculate_window_mean, args=(surface_threshold, data))
    window = window_means.iloc[((window_means.offset_mean.diff()/window_means.window_size).diff()/window_means.window_size).idxmin()].window_size.astype(int)

    data['depth_offset'] = data[data.depth < animal_length].depth.rolling(window).median()
    data.depth_offset = data.depth_offset.interpolate().fillna(0)
    data['corrected_depth'] = data.depth - data.depth_offset
    data['window_size'] = window
    corrected_data = pd.DataFrame()
    corrected_data['time'] = data.time
    corrected_data['depth'] = data.corrected_depth


    time_units = 'seconds since 1970-01-01'
    data.time = date2num(data.time.tolist(), units=time_units)
    xarray_data = xr.Dataset(data)
    xarray_data.variables['time'].attrs = {'units':time_units}
    xarray_data.variables['depth'].attrs = {'units':'meters', 'positive':'down'}
    xarray_data.to_netcdf(aux_file, mode='w', encoding=zlib_encoding(xarray_data))
    xarray_data.close()

    return corrected_data
