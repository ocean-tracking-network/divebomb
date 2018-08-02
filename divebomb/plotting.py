import os

import colorlover as cl
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as py
import xarray as xr
from netCDF4 import Dataset, num2date


def plot_from_nc(folder,
                 cluster,
                 dive_id,
                 ipython_display=True,
                 type='dive',
                 filename='index.html',
                 at_depth_threshold=0.15):
    """
    :param folder: the path to the results folder contianing the cluster
        folders
    :param cluster: the number of the cluster of the dive
    :param dive_id: the number of of the dive
    :param type: a string of either either ``dive`` or ``deepdive``
    :param ipython_display: a boolean indicating whether or not to show the
        dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a
        notebook
    :param at_depth_threshold: a value from 0 - 1 indicating distance from the
        bottom of the dive at which the animal is considered to be at depth

    :return: a plotly line chart of the dive

    """
    if type == 'deepdive':
        return plot_deepdive_from_nc(folder, cluster, dive_id, ipython_display,
                                     filename, at_depth_threshold)
    else:
        return plot_dive_from_nc(folder, cluster, dive_id, ipython_display,
                                 filename)


def plot_dive_from_nc(folder,
                      cluster,
                      dive_id,
                      ipython_display=True,
                      filename='index.html',
                      at_depth_threshold=0.15,
                      title='Clusters'):
    """
    :param folder: the path to the results folder contianing the cluster
        folders
    :param cluster: the number of the cluster of the dive
    :param dive_id: the number of of the dive
    :param ipython_display: a boolean indicating whether or not to show the
        dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a
        notebook
    :param at_depth_threshold: a value from 0 - 1 indicating distance from the
        bottom of the dive at which the animal is considered to be at depth
    :param title: string title of plot

    :return: a plotly line chart of the dive

    """
    dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder, cluster, dive_id)
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
        name='Surface')

    # Get and set the bottom data
    bottom_data = data[(data.time >= rootgrp.bottom_start) & (
        data.time <= (rootgrp.bottom_start + rootgrp.td_bottom_duration))]
    bottom = go.Scatter(
        x=num2date(bottom_data.time.tolist(), units=rootgrp.time_units),
        y=bottom_data.depth,
        mode='lines',
        name='Bottom')

    descent_data = data[data.time <= bottom_data.time.min()]
    descent = go.Scatter(
        x=num2date(descent_data.time.tolist(), units=rootgrp.time_units),
        y=descent_data.depth,
        mode='lines',
        name='Descent')

    # Get and set the ascent data
    ascent_data = data[
        (data.time >= bottom_data.time.max()) &
        (data.time <= surface_data.time.min())
    ]
    ascent = go.Scatter(
        x=num2date(ascent_data.time.tolist(), units=rootgrp.time_units),
        y=ascent_data.depth,
        mode='lines',
        name='Ascent')

    layout = go.Layout(
        title='Dive {} from Cluster {}'.format(rootgrp.dive_id,
                                               rootgrp.cluster),
        xaxis=dict(title='Time'),
        yaxis=dict(title='Depth in Meters', autorange='reversed'))
    rootgrp.close()

    plot_data = [descent, bottom, ascent, surface]
    fig = go.Figure(data=plot_data, layout=layout)

    if ipython_display:
        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        return py.plot(fig, filename=filename)


def plot_deepdive_from_nc(folder,
                          cluster,
                          dive_id,
                          ipython_display=True,
                          filename='index.html',
                          at_depth_threshold=0.15):
    """
    :param folder: the path to the results folder contianing the cluster
        folders
    :param cluster: the number of the cluster of the dive
    :param dive_id: the number of of the dive
    :param ipython_display: a boolean indicating whether or not to show the
        dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a
        notebook
    :param at_depth_threshold: a value from 0 - 1 indicating distance from the
        bottom of the dive at which the animal is considered to be at depth

    :return: a plotly line chart of the dive

    """
    dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder, cluster, dive_id)
    rootgrp = Dataset(dive_file)
    data = pd.DataFrame()
    data['time'] = rootgrp.variables['time'][:]
    data['depth'] = rootgrp.variables['depth'][:]
    units = rootgrp.variables['time'].units
    at_depth_data = data[data.depth > (data.depth.max() - (
        (data.depth.max() - data.depth.min()) * at_depth_threshold))]
    pre_depth_data = data[(data.depth < (data.depth.max() - (
        (data.depth.max() - data.depth.min()) * at_depth_threshold))) &
        (data.time <= at_depth_data.time.min())]
    post_depth_data = data[(data.depth < (data.depth.max() - (
        (data.depth.max() - data.depth.min()) * at_depth_threshold))) &
        (data.time >= at_depth_data.time.max())]

    pre_depth_data = pre_depth_data.append(at_depth_data.head(1))
    post_depth_data = post_depth_data.append(at_depth_data.tail(1))
    post_depth_data.sort_values('time', inplace=True)

    pre_depth = go.Scatter(
        x=num2date(pre_depth_data.time.tolist(), units=units),
        y=pre_depth_data.depth,
        mode='lines+markers',
        name='Pre Depth')

    at_depth = go.Scatter(
        x=num2date(at_depth_data.time.tolist(), units=units),
        y=at_depth_data.depth,
        mode='lines+markers',
        name='At Depth')

    post_depth = go.Scatter(
        x=num2date(post_depth_data.time.tolist(), units=units),
        y=post_depth_data.depth,
        mode='lines+markers',
        name='Post Depth')

    layout = go.Layout(
        title='Dive {} from Cluster {}'.format(rootgrp.dive_id,
                                               rootgrp.cluster),
        xaxis=dict(title='Time'),
        yaxis=dict(title='Depth in Meters', autorange='reversed'))
    rootgrp.close()
    plot_data = [pre_depth, post_depth, at_depth]
    fig = go.Figure(data=plot_data, layout=layout)
    if ipython_display:
        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        return py.plot(fig, filename=filename)


def cluster_summary_plot(folder,
                         ipython_display=True,
                         filename='index.html',
                         title='Dive Cluster Summary',
                         scale={
                             'depth': False,
                             'time': False
                         }):
    """
    :param folder: the path to the results folder contianing the cluster
        folders
    :param ipython_display: a boolean indicating whether or not to show the
        dive in a notebook
    :param filename: the filename to save the dive to if it is not shown in a
        notebook
    :param title: the displaye title of the plot

    :return: a plotly graph summary of all of the dive clusters

    """

    dataset = xr.open_dataset(os.path.join(folder, 'all_profiled_dives.nc'))
    df = dataset.to_dataframe().reset_index(drop=True)
    df.sort_values('dive_start', inplace=True)
    df['dive_id'] = df.index + 1

    xaxis = 'time'
    xaxis_title = 'Time in Seconds into Dive'

    yaxis = 'depth'
    yaxis_title = 'Depth in Meters'

    dive_data = pd.DataFrame()
    for group, data in df.groupby('cluster'):
        for index, row in data.iterrows():
            dive_file = '%s/cluster_%d/dive_%05d.nc' % (folder, row.cluster,
                                                        row.dive_id)
            rootgrp = Dataset(dive_file)
            single_dive_data = pd.DataFrame()
            single_dive_data['depth'] = rootgrp.variables['depth'][:]
            single_dive_data['time'] = rootgrp.variables['time'][:]
            single_dive_data['time'] = single_dive_data['time'] - \
                single_dive_data['time'].min()
            if 'time' in scale.keys() and scale['time']:
                single_dive_data['progress_into_dive'] = round(
                    single_dive_data.time / single_dive_data.time.max() * 100,
                    0)
                xaxis = 'progress_into_dive'
                xaxis_title = 'Progress Through Dive (%)'

            if 'depth' in scale.keys() and scale['depth']:
                single_dive_data['dive_relative_depth_percentage'] = round(
                    single_dive_data.depth / single_dive_data.depth.max() *
                    100, 0)
                yaxis = 'dive_relative_depth_percentage'
                yaxis_title = 'Depth (%) Relative to the Dive'
            single_dive_data['cluster'] = rootgrp.cluster
            dive_data = dive_data.append(single_dive_data)
            rootgrp.close()

    aggregated_data = dive_data.groupby([xaxis, 'cluster']).agg(
        ['min', 'mean', 'max', 'median', 'count']).reset_index(level=[0, 1])

    plot_data = []
    colors = cl.scales[str(len(
        aggregated_data.cluster.unique()))]['qual']['Paired']

    for cluster in aggregated_data.cluster.unique():

        line_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster][xaxis],
            y=aggregated_data[aggregated_data.cluster == cluster][yaxis][
                'min'],
            mode='lines',
            legendgroup='cluster' + str(cluster),
            name='Cluster ' + str(cluster) + " Min Depth",
            line=go.scatter.Line(color=colors[cluster], dash='dash'))
        plot_data.append(line_trace)

        fill_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster][xaxis],
            y=aggregated_data[aggregated_data.cluster == cluster][yaxis][
                'max'],
            fill='tonexty',
            mode='lines',
            legendgroup='cluster' + str(cluster),
            fillcolor=colors[cluster].replace(')', ',0.3)').replace(
                'rgb', 'rgba'),
            name='Cluster ' + str(cluster) + ' Possible Range',
            line=go.scatter.Line(width=0, color=colors[cluster]),
        )
        plot_data.append(fill_trace)

        line_trace = go.Scatter(
            x=aggregated_data[aggregated_data.cluster == cluster][xaxis],
            y=aggregated_data[aggregated_data.cluster == cluster][yaxis][
                'mean'],
            mode='lines',
            legendgroup='cluster' + str(cluster),
            name='Cluster ' + str(cluster) + " Average Depth",
            line=go.scatter.Line(color=colors[cluster]),
        )
        plot_data.append(line_trace)

    layout = go.Layout(
        title=title,
        xaxis=dict(title=xaxis_title, range=[0, aggregated_data[xaxis].max()]),
        yaxis=dict(title=yaxis_title, autorange='reversed'))
    py.init_notebook_mode()
    fig = go.Figure(data=plot_data, layout=layout)
    if ipython_display:
        py.init_notebook_mode()
        return py.iplot(fig)
    else:
        return py.plot(fig, filename=filename)
