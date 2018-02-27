import plotly.offline as py
import plotly.graph_objs as go
from netCDF4 import Dataset, num2date
import pandas as pd
import os

def plot_from_nc(folder, cluster, dive_id, ipython_display=True, filename=None):
    dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder,cluster,dive_id)
    rootgrp = Dataset(dive_file)
    data = pd.DataFrame()
    data['time'] = rootgrp.variables['time'][:]
    data['depth'] = rootgrp.variables['depth'][:]


    descent_data = data[data.time <= rootgrp.bottom_start]
    descent = go.Scatter(
        x=num2date(descent_data.time.tolist(), units=rootgrp.time_units),
        y=descent_data.depth,
        mode='lines',
        name='Descent'
    )

    # Get and set the bottom data
    bottom_data = data[(data.time >= rootgrp.bottom_start) & (
        data.time <= (rootgrp.bottom_start + rootgrp.td_bottom_duration))]
    bottom = go.Scatter(
        x=num2date(bottom_data.time.tolist(), units=rootgrp.time_units),
        y=bottom_data.depth,
        mode='lines',
        name='Bottom'
    )

    # Get and set the ascent data
    ascent_data = data[(data.time >= (rootgrp.bottom_start + rootgrp.td_bottom_duration)) & (
        data.time <= (data.time.max() - rootgrp.td_surface_duration))]
    ascent = go.Scatter(
        x=num2date(ascent_data.time.tolist(), units=rootgrp.time_units),
        y=ascent_data.depth,
        mode='lines',
        name='Ascent'
    )

    # Get and set the surface data
    surface_data = data[data.time >= (
        data.time.max() - rootgrp.td_surface_duration)]

    surface = go.Scatter(
        x=num2date(surface_data.time.tolist(), units=rootgrp.time_units),
        y=surface_data.depth,
        mode='lines',
        name='Surface'
    )

    layout = go.Layout(title='Dive {} from Cluster {}'.format(rootgrp.dive_id,rootgrp.cluster),xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))
    rootgrp.close()

    plot_data = [descent, bottom, ascent, surface]
    fig = go.Figure(data=plot_data, layout=layout)
    return py.iplot(fig)
