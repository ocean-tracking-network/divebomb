import plotly.offline as py
import plotly.graph_objs as go
from netCDF4 import Dataset, num2date
import pandas as pd
import os
import xarray as xr
import colorlover as cl

def plot_from_nc(folder, cluster, dive_id, ipython_display=True, filename='index.html'):
    """
    :param folder: the path to the results folder contianing the cluster folders
    :param cluster: the number of the cluster of the dive
    :param dive_id: the number of of the dive
    :param ipython_display: a boolean indicating whether or not to show the dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a notebook

    :return: a plotly line chart of the dive

    """
    dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder,cluster,dive_id)
    rootgrp = Dataset(dive_file)
    data = pd.DataFrame()
    data['time'] = rootgrp.variables['time'][:]
    data['depth'] = rootgrp.variables['depth'][:]

    # Get and set the surface data
    surface_data = data[data.time >= (
        data.time.max() - rootgrp.td_surface_duration)]

    surface = go.Scatter(
        x=num2date(surface_data.time.tolist(), units=rootgrp.time_units),
        y=surface_data.depth,
        mode='lines',
        name='Surface'
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

    descent_data = data[data.time <= bottom_data.time.min()]
    descent = go.Scatter(
        x=num2date(descent_data.time.tolist(), units=rootgrp.time_units),
        y=descent_data.depth,
        mode='lines',
        name='Descent'
    )

    # Get and set the ascent data
    ascent_data = data[(data.time >= bottom_data.time.max()) & (
        data.time <= surface_data.time.min())]
    ascent = go.Scatter(
        x=num2date(ascent_data.time.tolist(), units=rootgrp.time_units),
        y=ascent_data.depth,
        mode='lines',
        name='Ascent'
    )


    layout = go.Layout(title='Dive {} from Cluster {}'.format(rootgrp.dive_id,rootgrp.cluster),xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))
    rootgrp.close()

    plot_data = [descent, bottom, ascent, surface]
    fig = go.Figure(data=plot_data, layout=layout)

    if ipython_display:
        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        return py.plot(fig, filename=filename)


def cluster_summary_plot(folder, ipython_display=True, filename='index.html',title='Dive Cluster Summary'):
    """
    :param folder: the path to the results folder contianing the cluster folders
    :param ipython_display: a boolean indicating whether or not to show the dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a notebook
    :param title: the displaye title of the plot

    :return: a plotly graph summary of all of the dive clusters

    """

    dataset = xr.open_dataset(os.path.join(folder, 'all_profiled_dives.nc'))
    df = dataset.to_dataframe().reset_index(drop=True)
    df.sort_values('dive_start', inplace=True)
    df['dive_id'] = df.index+1


    dive_data = pd.DataFrame()
    for group, data in df.groupby('cluster'):
        for index, row in data.iterrows():
            dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder,row.cluster,row.dive_id)
            rootgrp= Dataset(dive_file)
            single_dive_data = pd.DataFrame()
            single_dive_data['time'] = rootgrp.variables['time'][:]
            single_dive_data['time'] = single_dive_data['time'] - single_dive_data['time'].min()
            single_dive_data['depth'] = rootgrp.variables['depth'][:]
            single_dive_data['cluster'] = rootgrp.cluster
            dive_data = dive_data.append(single_dive_data)
            rootgrp.close()
    aggregated_data = dive_data.groupby(['time', 'cluster']).agg(['min','mean','max', 'median']).reset_index(level=[0,1])

    plot_data = []
    colors = cl.scales[str(len(aggregated_data.cluster.unique()))]['qual']['Paired']

    for cluster in aggregated_data.cluster.unique():

        line_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster]['time'],
            y=aggregated_data[aggregated_data.cluster == cluster]['depth']['min'],
            mode='lines',
            legendgroup= 'cluster'+str(cluster),
            name='Cluster '+str(cluster)+ " Min Depth",
            line=go.Line(color=colors[cluster], dash = 'dash'),
        )
        plot_data.append(line_trace)

        fill_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster]['time'],
            y=aggregated_data[aggregated_data.cluster == cluster]['depth']['max'],
            fill='tonexty',
            legendgroup= 'cluster'+str(cluster),
            fillcolor=colors[cluster].replace(')', ',0.3)').replace('rgb', 'rgba'),
            name='Cluster '+str(cluster) +' Possible Range',
            line=go.Line(color='transparent'),
        )
        plot_data.append(fill_trace)

        line_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster]['time'],
            y=aggregated_data[aggregated_data.cluster == cluster]['depth']['mean'],
            mode='lines',
            legendgroup= 'cluster'+str(cluster),
            name='Cluster '+str(cluster)+ " Average Depth",
            line=go.Line(color=colors[cluster]),
        )
        plot_data.append(line_trace)


    layout = go.Layout(title=title,xaxis=dict(title='Time in Seconds', range=[0, 3600]), yaxis=dict(title='Depth in Meters',autorange='reversed'))
    py.init_notebook_mode()
    fig = go.Figure(data=plot_data, layout=layout)
    if ipython_display:
        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        return py.plot(fig, filename=filename)
