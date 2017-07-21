'''
Divebomb
---------------------------------
Divebomb is a python package that uses pandas to divide a timeseries of depths into idividual dives.

Each dive is then profiled with the following attributes:
    max_depth -
    dive_start - the timestamp of the first point in the dive.
    bottom_start - the timestamp of the first point in the dive when the animal is at depth.
    td_bottom_duration - a timedelta object containing the duration of the time the animal is at depth in seconds.
    td_descent_duration - a timedelta object containing the duration of the time the animal is descending in seconds.
    td_ascent_duration - a timedelta object containing the duration of the time the animal is ascending in seconds.
    td_surface_duration - a timedelta object containing the duration of the time the animal is at the surface in seconds.
    bottom_variance - the variance of the depth while the animal is at the bottom of the dive.
    descent_velocity - the average velocity of the descent.
    ascent_velocity the average velocity of the descent.
    shape - the text calssification of the dive using the DiveShape enumeration.


'''

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

pd.options.mode.chained_assignment = None

units = 'seconds since 1970-01-01'

'''
display_dive()
--------------
This function just takes the index, the data, and the starts and displays the dive using plotly.
'''
def display_dive(index, data, starts):
    index = int(index)
    print str(starts.loc[index, 'start_block']) + ":" + str(starts.loc[index, 'end_block'])
    dive_profile = Dive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']])
    return dive_profile.plot()

'''
profile_dives()
--------------
This function takes the data and generates the first and second derivatives to find the starting points of the dives. The starting points
are found by looking at the change in the second derivative, the change in depth, and the surface threshold. Short dives of less than
five points are ignored. The starting points, along with the original data can then be modeled into dives using the Dive class. The function
will either display the dives in an iPython notebook or export the data to a folder of CSVs.
'''
def profile_dives(data, folder=None, columns={'depth': 'depth', 'time': 'time'}, acceleration_threshold=0.015, surface_threshold=3.0, ipython_display_mode=False):
    if data[columns['time']].dtypes != np.float64:
        data[columns['time']] = date2num(pd.to_datetime(data[columns['time']]).tolist(),units=units)
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

    # Remove dives shorter than five points and reset the index
    starts = starts[(starts.end_block - starts.start_block) >= 5]
    starts.reset_index(inplace=True, drop=True)
    
    # Use the interact widget to display the dives using a slider to indicate the index.
    if ipython_display_mode:
        py.init_notebook_mode()
        return interact(display_dive, index=widgets.IntSlider(min=0, max=starts.index.max(), step=1, value=0, layout=Layout(width='100%')), data=fixed(data), starts=fixed(starts))
    elif folder is None:
        return 'Error: You must provide a folder name or set ipython_display_mode=True'
    else:
        # If the user indicates that the results should be stored iterate through and add the dives to a dataframe
        dives = pd.DataFrame()
        for index, row in starts.iterrows():
            dive_profile = Dive(data[starts.loc[index, 'start_block']:starts.loc[index, 'end_block']], surface_threshold=surface_threshold)
            dives = dives.append(dive_profile.to_dict(), ignore_index=True)

        # Create the folder and save the files
        if not os.path.exists(folder):
            os.makedirs(folder)
        data.to_csv(folder + '/original_dive_data.csv', index=False)
        dives.to_csv(folder + '/generated_dive_profiles.csv', index=False)
        starts.to_csv(folder + '/original_dive_data_starting_points.csv', index=False)

        # Return the three datasets back to the user
        return {'data': data, 'dives': dives, 'starts': starts}
