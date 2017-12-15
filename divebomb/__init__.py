import pandas as pd
from Dive import Dive
import os
import numpy as np
import __future__
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
import ipywidgets as widgets
import plotly.offline as py
import plotly.graph_objs as go
from netCDF4 import date2num
import math

pd.options.mode.chained_assignment = None

units = 'seconds since 1970-01-01'


def display_dive(index, data, starts,  surface_threshold):
    """
    This function just takes the index, the data, and the starts and displays the dive using plotly.

    :param index: the index of the dive profile to plot
    :param data: the dataframe of the original dive data
    :param starts: the dataframe of the dive starts
    :param surface_threshold: the calculated surface threshold based on animal length
    :return: a dive plot from plotly

    """

    index = int(index)
    print str(starts.loc[index, 'start_block']) + ":" + str(starts.loc[index, 'end_block'])
    dive_profile = Dive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']],  surface_threshold=surface_threshold)
    return dive_profile.plot()


def profile_dives(data, folder=None, columns={'depth': 'depth', 'time': 'time'}, acceleration_threshold=0.015, animal_length=3.0, ipython_display_mode=False):
    """
    profiles the dives

    :param data: a dataframe needing a time and a depth column
    :param folder: a parent folder to write out to
    :param columns: column renaming dictionary if needed
    :param acceleration_threshold: the minimu change in acceleration to determine the start point
    :param  animal_length: length of the animal in meters
    :param  ipython_display_mode: whether or not to display the dives
    :return: three dataframes for the dive profiles, start blocks, and the original data

    """

    # Get surface thresholdbased on animal length
    surface_threshold = math.cos(math.radians(45)) * animal_length

    # drop all columns in the dataframe that aren't time or depth
    for k, v in columns.iteritems():
        if k != v:
            data[k] = data[v]
            data.drop(v, axis=1)
    # Convert time to seconds since
    if data[columns['time']].dtypes != np.float64:
        data[columns['time']] = date2num(pd.to_datetime(data[columns['time']]).tolist(), units=units)

    # Sort data into a time series and create the 1st and 2nd derivatives (velocity and acceleration)
    data = data.sort_values(by=columns['time'])
    data['velocity'] = data[columns['depth']].diff() / data[columns['time']].diff()
    data['acceleration'] = (data.velocity.diff()/data[columns['time']].diff())

    # Generate the depth difference, acceleration lead, and depth lead
    data['depth_diff'] = data.depth.diff()
    data['accel_lead'] = data.acceleration.shift(-1)
    data['depth_lead'] = data.depth_diff.shift(-1)


    # Filter the data byt the next change in acceleration, the next change in depth, and the current dpeth to find the possible starting points
    starts = data[(data['accel_lead'] >= acceleration_threshold) & (data.depth_lead > 0) & (data[columns['depth']] <= surface_threshold)]

    # Store the starting index and end index for each of the dives
    starts['start_block'] = starts.index
    starts['end_block'] = starts.start_block.shift(-1) + 1
    starts.end_block.fillna(data.index.max(), inplace=True)
    starts.end_block = starts.end_block.astype(int)

    for index, row in starts.iterrows():
        starts.loc[index, 'max_depth'] = data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']].depth.max()


    starts = starts[(starts.max_depth > surface_threshold)]
    starts.drop(['start_block', 'end_block', 'max_depth'], axis=1, inplace=True)
    starts['time_diff'] = starts.time.diff()
    starts = starts[(starts.time_diff >= 30)]

    # Store the starting index and end index for each of the dives
    starts['start_block'] = starts.index
    starts['end_block'] = starts.start_block.shift(-1) + 1

    starts.end_block.fillna(data.index.max(), inplace=True)
    starts.end_block = starts.end_block.astype(int)
    # Remove dives shorter than five points and reset the index

    starts.reset_index(inplace=True, drop=True)

    # Use the interact widget to display the dives using a slider to indicate the index.
    if ipython_display_mode:
        py.init_notebook_mode()
        return interact(display_dive, index=widgets.IntSlider(min=0, max=starts.index.max(), step=1, value=0, layout=Layout(width='100%')), data=fixed(data), starts=fixed(starts), surface_threshold=fixed(surface_threshold))
    elif folder is None:
        return 'Error: You must provide a folder name or set ipython_display_mode=True'
    else:
        # If the user indicates that the results should be stored iterate through and add the dives to a dataframe
        dives = pd.DataFrame()
        for dive in profiles:
            dives = dives.append(dive.to_dict(), ignore_index=True)

        # Create the folder and save the files
        if not os.path.exists(folder):
            os.makedirs(folder)
        data.to_csv(folder + '/original_dive_data.csv', index=False)
        dives.to_csv(folder + '/generated_dive_profiles.csv', index=False)
        starts.to_csv(folder + '/original_dive_data_starting_points.csv', index=False)

        # Return the three datasets back to the user
        return {'data': data, 'dives': dives, 'starts': starts}
