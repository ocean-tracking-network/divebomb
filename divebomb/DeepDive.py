from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
import copy
import sys
from netCDF4 import Dataset, num2date, date2num
import peakutils as pk

units = 'seconds since 1970-01-01'


class DeepDive:

    def __init__(self, data, columns={'depth': 'depth', 'time': 'time'}):

        self.sufficient=True
        if data[columns['time']].dtypes != np.float64:
            data.time = date2num(data.time.tolist(),units=units)

        self.data = data.sort_values('time').reset_index(drop=True)
        for k, v in columns.items():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v, axis=1)

        self.max_depth = self.data.depth.max()
        self.min_depth = self.data.depth.min()
        self.dive_start = self.data.time.min()
        self.dive_end = self.data.time.max()
        self.total_duration = self.data.time.max() - self.data.time.min()
        self.depth_variance = np.std(self.data.depth)
        self.average_vertical_velocity = np.absolute(((self.data.depth.diff()/self.data.time.diff()))).mean()
        self.average_descent_velocity = self.get_average_descent_velocity()
        self.average_ascent_velocity = self.get_average_ascent_velocity()
        self.number_of_descent_transitions = len(self.data[(self.data.depth.diff()/self.data.time.diff()) > 0])
        self.number_of_ascent_transitions = len(self.data[(self.data.depth.diff()/self.data.time.diff()) > 0])
        self.total_descent_distance_traveled = self.get_descent_vertical_distance()
        self.total_ascent_distance_traveled = self.get_ascent_vertical_distance()
        self.peaks = self.get_peaks()
        self.overall_change_in_depth =  self.data.depth.diff().sum()
        self.time_at_depth = self.get_time_at_depth()
        self.time_pre_depth = self.get_time_pre_depth()
        self.time_post_depth = self.get_time_post_depth()

    def get_peaks(self):
        """
        :return: number of peaks found within a dive
        """
        peak_thres = (1 - (self.data.depth.min()/ self.data.depth.max()))
        peaks = pk.indexes(self.data.depth*(-1), thres=min([0.1, peak_thres]), min_dist=max((10/self.data.time.diff().mean()),3))
        self.peaks = len(peaks)
        return self.peaks

    def get_time_at_depth(self):
        time=0
        dive = self.data.copy(deep=True)
        dive['time_diff']= dive.time.diff()
        time_data = dive[dive.depth > (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))].tail(-1)
        if len(time_data) != 0:
            time = time_data.time_diff.sum()
        del dive
        return time

    def get_time_at_depth(self):
        time=0
        dive = self.data.copy(deep=True)
        dive['time_diff']= dive.time.diff()
        at_depth_data = dive[dive.depth > (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))]
        pre_depth_data = dive[(dive.depth < (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))) & (dive.time <= at_depth_data.time.min())]


        pre_depth_data =  pre_depth_data.append(at_depth_data.head(1))
        post_depth_data =  post_depth_data.append(at_depth_data.tail(1))
        post_depth_data.sort_values('time', inplace=True)
        del dive
        return time

    def get_descent_vertical_distance(self):
        dive = self.data.copy(deep=True)
        dive['depth_diff'] = dive.depth.diff()
        distance = np.absolute(dive[(dive.depth_diff > 0)].depth_diff.sum())
        del dive
        return distance

    def get_ascent_vertical_distance(self):
        dive = self.data.copy(deep=True)
        dive['depth_diff'] = dive.depth.diff()
        distance = np.absolute(dive[(dive.depth_diff < 0)].depth_diff.sum())
        del dive
        return distance

    def get_average_ascent_velocity(self):
        dive = self.data.copy(deep=True)
        dive['velocity'] = dive.depth.diff()/dive.time.diff()
        velocity = np.absolute(dive[dive.velocity < 0].velocity.mean())
        del dive
        return velocity

    def get_average_descent_velocity(self):
        dive = self.data.copy(deep=True)
        dive['velocity'] = dive.depth.diff()/dive.time.diff()
        velocity = np.absolute(dive[dive.velocity > 0].velocity.mean())
        del dive
        return velocity

    def to_dict(self):
        """

        :return: a dictionary of the dive profile
        """
        dive = copy.deepcopy(self.__dict__)
        del dive['data']
        return dive

    def plot(self):

        """

        :return: a plotly graph showing the phases of the dive
        """
        # Set the data to plot the segments of the dive
        if self.sufficient:
            # Get and set the descent data

            dive = self.data.copy(deep=True)
            dive['time_diff']= dive.time.diff()

            at_depth_data = dive[dive.depth > (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))]
            pre_depth_data = dive[(dive.depth < (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))) & (dive.time <= at_depth_data.time.min())]
            post_depth_data = dive[(dive.depth < (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15)))& (dive.time >= at_depth_data.time.max())]


            pre_depth_data =  pre_depth_data.append(at_depth_data.head(1))
            post_depth_data =  post_depth_data.append(at_depth_data.tail(1))
            post_depth_data.sort_values('time', inplace=True)

            pre_depth = go.Scatter(
                x=num2date(pre_depth_data.time.tolist(), units=units),
                y=pre_depth_data.depth,
                mode='lines+markers',
                name='Pre Depth'
            )

            at_depth = go.Scatter(
                x=num2date(at_depth_data.time.tolist(), units=units),
                y=at_depth_data.depth,
                mode='lines+markers',
                name='At Depth'
            )

            post_depth = go.Scatter(
                x=num2date(post_depth_data.time.tolist(), units=units),
                y=post_depth_data.depth,
                mode='lines+markers',
                name='Post Depth'
            )

            layout = go.Layout(title='Dive starting at {}'.format(num2date(self.dive_start, units=units)),
                               xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))
            plot_data = [pre_depth, post_depth, at_depth]
            fig = go.Figure(data=plot_data, layout=layout)
            return py.iplot(fig)
        else:
            print("Insufficient data to plot.")
