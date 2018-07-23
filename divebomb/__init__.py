
__author__ = "Alex Nunes"
__credits__ = ["Alex Nunes", "Fran Broell"]
__license__ = "GPLv2"
__version__ = "0.3.0"
__maintainer__ = "Alex Nunes"
__email__ = "anunes@dal.ca"
__status__ = "Development"


import pandas as pd
from divebomb.Dive import Dive
from divebomb.DeepDive import DeepDive
import os, shutil
import numpy as np
import __future__
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
import ipywidgets as widgets
import plotly.offline as py
import plotly.graph_objs as go
from netCDF4 import date2num, num2date, Dataset
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
import xarray as xr
import math
import peakutils as pku

pd.options.mode.chained_assignment = None

units = 'seconds since 1970-01-01'


def display_dive(index, data, starts, type='Dive', surface_threshold=0):
    """
    This function just takes the index, the data, and the starts and displays the dive using plotly.
    It is used as a helper method for viewing the dives if ``ipython_display`` is ``True`` in ``profile_dives()``.

    :param index: the index of the dive profile to plot
    :param data: the dataframe of the original dive data
    :param starts: the dataframe of the dive starts
    :param surface_threshold: the calculated surface threshold based on animal length
    :return: a dive plot from plotly

    """

    index = int(index)
    print(str(starts.loc[index, 'start_block']) + ":" + str(starts.loc[index, 'end_block']))
    if type == 'DeepDive':
        dive_profile = DeepDive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']])
    else:
        dive_profile = Dive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']],  surface_threshold=surface_threshold)
    return dive_profile.plot()

def cluster_dives(dives):
    """
    This function takes advantage of sklearn and reduces the dimensionality
    with Principal Component Analysis, finds the optimal number of n_clusters
    using Gaussian Mixed Models and the Bayesion Information Criterion, then
    uses Agglomerative Clustering on the dives profiles to group them.

    :param dives: a pandas DataFrame of dive attributes

    :return: the clustered dives, the PCA loadings matrix,
             and the PCA output matrix

    """
    # Subset the data
    dataset = dives.fillna(0)
    # dataset = dataset[['ascent_velocity',
    #                   'descent_velocity',
    #                   'bottom_variance',
    #                   'td_ascent_duration',
    #                   'td_bottom_duration',
    #                   'td_descent_duration',
    #                   'dive_duration',
    #                   'peaks',
    #                   'no_skew',
    #                   'left_skew',
    #                   'right_skew']]
    dataset.drop(['dive_start', 'dive_end'], axis=1, inplace=True)
    if 'surface_threshold' in dataset.columns:
        dataset.drop('surface_threshold', axis=1, inplace=True)

    # Scale all values
    X = dataset.values
    sc_X = StandardScaler()
    X = sc_X.fit_transform(X)

    # Apply principle component analysis
    pca = PCA(n_components = 8)
    X = pca.fit_transform(X)

    # Get the loadings matrix
    loadings = pd.DataFrame(pca.components_).T
    loadings.reset_index(inplace=True)
    column_heading = ['component']
    for column in loadings.columns:
        if column != 'index':
            column_heading.append('PC_'+str(column))
    loadings.columns=column_heading
    loadings['component'] = dataset.columns

    # Get the PCA output matrix
    pca_output_matrix = pd.DataFrame(X)
    column_heading = []
    for column in pca_output_matrix.columns:
        if column != 'index':
            column_heading.append('PC_'+str(column))
    pca_output_matrix.columns = column_heading

    # Find the optimal number of clusters
    n_components = np.arange(1, 11)
    models = [GaussianMixture(n, covariance_type='full', random_state=0).fit(X) for n in n_components]
    bics = y = [m.bic(X) for m in models]
    diffs = np.diff(bics).tolist()
    n_clusters = (diffs.index(max(diffs[4:])))

    # Apply Agglomerative clustering
    hc = AgglomerativeClustering(n_clusters = n_clusters, affinity = 'euclidean', linkage = 'ward')
    y_hc = hc.fit_predict(X)
    dataset['cluster'] = y_hc

    clustered_dives = dives.join(dataset[['cluster']])
    return clustered_dives, loadings ,pca_output_matrix

def export_dives(dives, data, folder, is_surface_events=False):
    """
    This function exports each dive to its own netCDF file grouped by cluster

    :param dives: a Pandas DataFrame of dive profiles to export
    :param data: a Pandas dataframe of the original dive data
    :param folder: a string indicating the parent folder for the files and sub folders
    :param is_surface_events: a boolean indicating if the dive profiles are entirely surface events

    """
    for index, dive in dives.iterrows():
        filename = '%s/cluster_%d/dive_%05d.nc' % (folder,dive.cluster,(index+1))
        rootgrp = Dataset(filename, 'w')
        rootgrp.setncattr('dive_id',index+1)
        rootgrp.setncattr('is_surface_event', int(is_surface_events))
        rootgrp.setncattr('time_units', units)
        for key,value in dive.to_dict().items():
            try:
                if value.is_integer():
                    rootgrp.setncattr(key,int(value))
                else:
                    rootgrp.setncattr(key,value)
            except TypeError:
                rootgrp.setncattr(key, str(value))
        rootgrp.createDimension('time', None)

        time = rootgrp.createVariable("time","f8",("time",),zlib=True)
        time.units = units
        depth = rootgrp.createVariable("depth","f8",("time",),zlib=True)

        time[:] = data[rootgrp.dive_start:rootgrp.dive_end].time.tolist()
        depth[:] = data[rootgrp.dive_start:rootgrp.dive_end].depth.tolist()

        rootgrp.close()

def export_all_data(folder, data, dives, loadings, pca_output_matrix):
    # Export the dives to netCDF
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    for cluster in dives.cluster.unique():
        os.makedirs(folder+'/cluster_'+str(cluster))

    # export the dives
    data.set_index('time',inplace=True, drop=False)
    dives.dive_start = dives.dive_start.astype(int)
    dives.dive_end = dives.dive_end.astype(int)
    data.time = data.time.astype(int)
    export_dives(dives, data, folder)

    # Export the PCA Matrices
    pca_group = Dataset(folder+'/pca_matrices_data.nc', 'w')
    pca_loadings = pca_group.createGroup('pca_loadings')
    pca_output = pca_group.createGroup('pca_output')

    pca_group.createDimension('order', None)

    str_max = (loadings.component.str.len()).max()
    components = pca_loadings.createVariable("component",str,('order',), zlib=True)
    components = np.array(loadings.component.tolist(), 'S'+str(int(str_max)))
    pc={}
    for column in loadings.iloc[:, 1:].columns:
        pc[column] = pca_loadings.createVariable(column,'f8',('order',),zlib=True)
        pc[column][:] = loadings[column].tolist()

    for column in pca_output_matrix.columns:
        pc[column] = pca_output.createVariable(column,'f8',('order',),zlib=True)
        pc[column][:] = loadings[column].tolist()
    pca_group.close()

    # Write an overall summary netcdf
    xarray_data = xr.Dataset(dives)
    if 'bottom_start' in xarray_data.variables:
        xarray_data.variables['bottom_start'].attrs = {'units':units}
    xarray_data.variables['dive_end'].attrs = {'units':units}
    xarray_data.variables['dive_start'].attrs = {'units':units}
    xarray_data.to_netcdf(os.path.join(folder, "all_profiled_dives.nc"), mode='w')
    xarray_data.close()

def clean_dive_data(data, columns={'depth': 'depth', 'time': 'time'}):
    for k, v in columns.items():
        if k != v:
            data[k] = data[v]
            data.drop(v, axis=1)
    # Convert time to seconds since
    if data[columns['time']].dtypes != np.float64:
        data[columns['time']] = date2num(pd.to_datetime(data[columns['time']]).tolist(), units=units)

    return data

def get_dive_starting_points(data, is_surfacing_animal = True, dive_detection_sensitivity=None,
                            minimal_time_between_dives = 10, surface_threshold=0, columns={'depth': 'depth', 'time': 'time'}):

    # drop all columns in the dataframe that aren't time or depth
    data = clean_dive_data(data)

    data = data.sort_values(by=columns['time']).reset_index(drop=True)
    data['time_diff'] = data.time.diff()

    if is_surfacing_animal and dive_detection_sensitivity is None:
        dive_detection_sensitivity = 0.98
    elif dive_detection_sensitivity is None:
        dive_detection_sensitivity = 0.5

    starts = pku.indexes((data.depth*-1), thres=dive_detection_sensitivity, min_dist=(minimal_time_between_dives/data.time.diff().mean()))
    starts = data[data.index.isin(starts)]

    starts['start_block'] = starts.index
    starts['end_block'] = starts.start_block.shift(-1) + 1
    starts.end_block.fillna(data.index.max(), inplace=True)
    starts.end_block = starts.end_block.astype(int)

    # This line specidifcally looks for larg time gaps in the data and ignores them using the index
    starts.loc[starts.time_diff.shift(-1) > starts.time_diff.mode()[0], 'end_block'] = starts.end_block - 1

    if is_surfacing_animal:
        for index, row in starts.iterrows():
            starts.loc[index, 'max_depth'] = data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']].depth.max()
        surface_threshold = surface_threshold
        starts = starts[(starts.max_depth > surface_threshold)]
        starts.drop(['start_block', 'end_block', 'max_depth', 'time_diff'], axis=1, inplace=True)
        starts['time_diff'] = starts.time.diff()
        starts['start_block'] = starts.index
        starts['end_block'] = starts.start_block.shift(-1) + 1
        starts.end_block.fillna(data.index.max(), inplace=True)
        starts.end_block = starts.end_block.astype(int)
    starts.reset_index(drop=True, inplace=True)
    return starts

def profile_dives(data, folder=None, columns={'depth': 'depth', 'time': 'time'},
                    is_surfacing_animal = True, dive_detection_sensitivity=None, minimal_time_between_dives = 10,
                    surface_threshold=0, ipython_display_mode=False):
    """
    Calls the other functions to split and profile each dive. This function uses the
    ``divebomb.Dive`` class to prfoile the dives.

    :param data: a dataframe needing a time and a depth column
    :param folder: a parent folder to write out to
    :param columns: column renaming dictionary if needed
    :param acceleration_threshold: the minimu change in acceleration to determine the start point
    :param  animal_length: length of the animal in meters
    :param  ipython_display_mode: whether or not to display the dives
    :return: three dataframes for the dive profiles, start blocks, and the original data

    """

    starts = get_dive_starting_points(data,
                                    is_surfacing_animal=is_surfacing_animal,
                                    minimal_time_between_dives=minimal_time_between_dives,
                                    dive_detection_sensitivity=dive_detection_sensitivity,
                                    surface_threshold=surface_threshold,
                                    columns=columns)

    type='Dive'
    if not is_surfacing_animal:
        type='DeepDive'

    # Use the interact widget to display the dives using a slider to indicate the index.
    if ipython_display_mode:
        py.init_notebook_mode()
        return interact(display_dive, index=widgets.IntSlider(min=0, max=starts.index.max(), step=1, value=0,
                        layout=Layout(width='100%')), data=fixed(data), starts=fixed(starts), type=fixed(type),
                        surface_threshold=fixed(surface_threshold))
    elif folder is None:
        return 'Error: You must provide a folder name or set ipython_display_mode=True'
    else:
        dives = pd.DataFrame()
        if type == 'DeepDive':
            for index, row in starts.iterrows():
                dive_profile = DeepDive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']])
                dives = dives.append(dive_profile.to_dict(), ignore_index=True)
        else:
            for index, row in starts.iterrows():
                dive_profile = Dive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']], surface_threshold=surface_threshold)
                dives = dives.append(dive_profile.to_dict(), ignore_index=True)

        dives, loadings, pca_output_matrix = cluster_dives(dives)

        export_all_data(folder, data, dives, loadings, pca_output_matrix)
        # # Export the dives to netCDF
        # if os.path.exists(folder):
        #     shutil.rmtree(folder)
        # os.makedirs(folder)
        #
        # for cluster in dives.cluster.unique():
        #     os.makedirs(folder+'/cluster_'+str(cluster))
        #
        # # export the dives
        # data.set_index('time',inplace=True, drop=False)
        # dives.dive_start = dives.dive_start.astype(int)
        # dives.dive_end = dives.dive_end.astype(int)
        # data.time = data.time.astype(int)
        # export_dives(dives ,data, folder)
        #
        # # Export the PCA Matrices
        # pca_group = Dataset(folder+'/pca_matrices_data.nc', 'w')
        # pca_loadings = pca_group.createGroup('pca_loadings')
        # pca_output = pca_group.createGroup('pca_output')
        #
        # pca_group.createDimension('order', None)
        #
        # str_max = (loadings.component.str.len()).max()
        # components = pca_loadings.createVariable("component",str,('order',), zlib=True)
        # components = np.array(loadings.component.tolist(), 'S'+str(int(str_max)))
        # pc={}
        # for column in loadings.iloc[:, 1:].columns:
        #     pc[column] = pca_loadings.createVariable(column,'f8',('order',),zlib=True)
        #     pc[column][:] = loadings[column].tolist()
        #
        # for column in pca_output_matrix.columns:
        #     pc[column] = pca_output.createVariable(column,'f8',('order',),zlib=True)
        #     pc[column][:] = loadings[column].tolist()
        # pca_group.close()
        #
        # # Write an overall summary netcdf
        # xarray_data = xr.Dataset(dives)
        # xarray_data.variables['bottom_start'].attrs = {'units':units}
        # xarray_data.variables['dive_end'].attrs = {'units':units}
        # xarray_data.variables['dive_start'].attrs = {'units':units}
        # xarray_data.to_netcdf(os.path.join(folder, "all_profiled_dives.nc"), mode='w')
        # xarray_data.close()


        # Return the three datasets back to the user
        return {'data': data, 'dives': dives}
