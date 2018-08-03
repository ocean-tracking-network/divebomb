import copy
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import peakutils as pk
import plotly.graph_objs as go
import plotly.offline as py
from netCDF4 import Dataset, date2num, num2date

units = 'seconds since 1970-01-01'


class DeepDive:
    """
    :ivar max_depth: the max depth in the dive
    :ivar min_depth: the max depth in the dive
    :ivar dive_start: the timestamp of the first point in the dive
    :ivar dive_end: the timestamp of the last point in the dive
    :ivar td_total_duration: a timedelta (in seconds since 1970-01-01)
        containing the duration of the dive
    :ivar depth_variance: the variance of the depth for the entire dive.
    :ivar average_vertical_velocity: the mean velocity of the animal over the
        entire dive with negative value indicating upward movement
    :ivar average_descent_velocity: the average velocity of any downward
        movement as positive value
    :ivar average_ascent_velocity: the average velocity of any upward movement
        as positive value
    :ivar number_of_descent_transitions: the number of times and animal moves
        descends any distance in the dive period
    :ivar number_of_ascent_transitions: the number of times and animal moves
        ascends any distance in the dive period
    :ivar total_descent_distance_traveled: the total absolute distance in
        meters in which the anaimal moves down
    :ivar total_ascent_distance_traveled: the total absolute distance in
        meters in which the anaimal moves up
    :ivar overall_change_in_depth: the difference between the minimum and
        maximum depth within the dive period
    :ivar td_time_at_depth: the duration in seconds at which the animal spends
        in the deepest part of the vertical movement (< 85% depth)
    :ivar td_time_pre_depth: the duration in seconds befor the deepest part of
        the vertical movement (< 85% depth)
    :ivar td_time_post_depth: the duration in seconds after the deepest part
        of the vertical movement (< 85% depth)
    :ivar peaks: the number of peaks found in the dive profile
    :ivar left_skew: a boolean of 1 or 0 indicating if the dive is left skewed
    :ivar right_skew: a boolean of 1 or 0 indicating if the dive is right
        skewed
    :ivar no_skew: a boolean of 1 or 0 indicating if the dive is not skewed

    """

    def __init__(self,
                 data,
                 columns={
                     'depth': 'depth',
                     'time': 'time'
                 },
                 at_depth_threshold=0.15):
        """
        :param data: the time and depth values for the dive
        :param columns: a dictionary of column mappings for the data
        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        """

        if data[columns['time']].dtypes != np.float64:
            data.time = date2num(data.time.tolist(), units=units)

        self.data = data.sort_values('time').reset_index(drop=True)
        for k, v in columns.items():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v, axis=1)

        self.max_depth = self.data.depth.max()
        self.min_depth = self.data.depth.min()
        self.dive_start = self.data.time.min()
        self.dive_end = self.data.time.max()
        self.td_total_duration = self.data.time.max() - self.data.time.min()
        self.depth_variance = np.std(self.data.depth)
        self.average_vertical_velocity = np.absolute(
            ((self.data.depth.diff() / self.data.time.diff()))).mean()
        self.average_descent_velocity = self.get_average_descent_velocity()
        self.average_ascent_velocity = self.get_average_ascent_velocity()

        self.number_of_descent_transitions = \
            len(self.data[(self.data.depth.diff() /
                           self.data.time.diff()) > 0])

        self.number_of_ascent_transitions = \
            len(self.data[(self.data.depth.diff() /
                           self.data.time.diff()) < 0])

        self.total_descent_distance_traveled =  \
            self.get_descent_vertical_distance()

        self.total_ascent_distance_traveled =   \
            self.get_ascent_vertical_distance()

        self.overall_change_in_depth = self.data.depth.diff().sum()
        self.td_time_at_depth = self.get_time_at_depth(at_depth_threshold)
        self.td_time_pre_depth = self.get_time_pre_depth(at_depth_threshold)
        self.td_time_post_depth = self.get_time_post_depth(at_depth_threshold)
        self.peaks = self.get_peaks()
        self.no_skew = 0
        self.right_skew = 0
        self.left_skew = 0
        self.set_skew()

    def get_peaks(self):
        """
        :return: number of peaks found within a dive
        """
        peak_thres = (1 - (self.data.depth.min() / self.data.depth.max()))
        peaks = pk.indexes(
            self.data.depth * (-1),
            thres=min([0.1, peak_thres]),
            min_dist=max((10 / self.data.time.diff().mean()), 3))
        self.peaks = len(peaks)
        return self.peaks

    def set_skew(self):
        """
        Sets the objects skew as left, right, or no skew
        """
        if self.td_time_pre_depth > self.td_time_post_depth:
            self.left_skew = 1
        elif self.td_time_post_depth > self.td_time_pre_depth:
            self.left_skew = 1
        else:
            self.no_skew = 1

    def get_time_at_depth(self, at_depth_threshold=0.15):
        """
        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        :return: the duration at depth in seconds
        """
        time = 0
        dive = self.data.copy(deep=True)
        dive['time_diff'] = dive.time.diff()
        time_data = dive[
            dive.depth > (dive.depth.max() - (
                (dive.depth.max() - dive.depth.min()) * at_depth_threshold)
            )
        ].tail(-1)
        if len(time_data) != 0:
            time = time_data.time_diff.sum()
        del dive
        return time

    def get_time_pre_depth(self, at_depth_threshold=0.15):
        """
        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        :return: the duration before depth in seconds
        """
        time = 0
        dive = self.data.copy(deep=True)
        dive['time_diff'] = dive.time.diff()
        at_depth_data = dive[
            dive.depth > (dive.depth.max() - (
                (dive.depth.max() - dive.depth.min()) * at_depth_threshold)
            )
        ].tail(-1)
        time_data = dive[dive.time < at_depth_data.time.min()]
        if len(time_data) != 0:
            time = time_data.time_diff.sum()
        del dive
        return time

    def get_time_post_depth(self, at_depth_threshold=0.15):
        """
        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        :return: the duration after depth in seconds
        """
        time = 0
        dive = self.data.copy(deep=True)
        dive['time_diff'] = dive.time.diff()
        at_depth_data = dive[
            dive.depth > (dive.depth.max() - (
                (dive.depth.max() - dive.depth.min()) * at_depth_threshold)
            )
        ].tail(-1)
        time_data = dive[dive.time > at_depth_data.time.max()]
        if len(time_data) != 0:
            time = time_data.time_diff.sum()
        del dive
        return time

    def get_descent_vertical_distance(self):
        """
        :return: the total vertical distance travelled upwards in meters
        """
        dive = self.data.copy(deep=True)
        dive['depth_diff'] = dive.depth.diff()
        distance = np.absolute(dive[(dive.depth_diff > 0)].depth_diff.sum())
        del dive
        return distance

    def get_ascent_vertical_distance(self):
        """
        :return: the total vertical distance travelled downwards in meters
        """
        dive = self.data.copy(deep=True)
        dive['depth_diff'] = dive.depth.diff()
        distance = np.absolute(dive[(dive.depth_diff < 0)].depth_diff.sum())
        del dive
        return distance

    def get_average_ascent_velocity(self):
        """
        :return: the average upwards velocity in m/s
        """
        dive = self.data.copy(deep=True)
        dive['velocity'] = dive.depth.diff() / dive.time.diff()
        velocity = np.absolute(dive[dive.velocity < 0].velocity.mean())
        del dive
        return velocity

    def get_average_descent_velocity(self):
        """
        :return: the average downwards velocity in m/s
        """
        dive = self.data.copy(deep=True)
        dive['velocity'] = dive.depth.diff() / dive.time.diff()
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
        dive = self.data.copy(deep=True)
        dive['time_diff'] = dive.time.diff()

        at_depth_data = dive[dive.depth > (dive.depth.max() - (
            (dive.depth.max() - dive.depth.min()) * at_depth_threshold))]
        pre_depth_data = dive[(dive.depth < (dive.depth.max() - (
            (dive.depth.max() - dive.depth.min()) * at_depth_threshold))) &
            (dive.time <= at_depth_data.time.min())]
        post_depth_data = dive[(dive.depth < (dive.depth.max() - (
            (dive.depth.max() - dive.depth.min()) * at_depth_threshold))) &
            (dive.time >= at_depth_data.time.max())]

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
            title='Dive starting at {}'.format(
                num2date(self.dive_start, units=units)),
            xaxis=dict(title='Time'),
            yaxis=dict(title='Depth in Meters', autorange='reversed'))
        plot_data = [pre_depth, post_depth, at_depth]
        fig = go.Figure(data=plot_data, layout=layout)
        return py.iplot(fig)
