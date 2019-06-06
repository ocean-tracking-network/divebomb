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


class Dive:
    """
    :ivar max_depth: the max depth in the dive
    :ivar dive_start: the timestamp of the first point in the dive
    :ivar dive_end: the timestamp of the last point in the dive
    :ivar bottom_start: the timestamp of the first point in the dive when the
        animal is at depth
    :ivar td_bottom_duration: a timedelta object containing the duration of the
        time the animal is at depth in seconds
    :ivar td_descent_duration: a timedelta object containing the duration of
        the time the animal is descending in seconds
    :ivar td_ascent_duration: a timedelta object containing the duration of the
        time the animal is ascending in seconds
    :ivar td_surface_duration: a timedelta object containing the duration of
        the time the animal is at the surface in seconds
    :ivar bottom_variance: the variance of the depth while the animal is at the
        bottom of the dive
    :ivar dive_variance: the variance of the depth for the entire dive.
    :ivar descent_velocity: the average velocity of the descent
    :ivar ascent_velocity: the average velocity of the ascent
    :ivar peaks: the number of peaks found in the dive profile
    :ivar left_skew: a boolean of 1 or 0 indicating if the dive is left skewed
    :ivar right_skew: a boolean of 1 or 0 indicating if the dive is right
        skewed
    :ivar no_skew: a boolean of 1 or 0 indicating if the dive is not skewed
    :ivar insufficient_data: a boolean indicating whether or not the profile
        could be completed

    """

    def __init__(self,
                 data,
                 columns={
                     'depth': 'depth',
                     'time': 'time'
                 },
                 surface_threshold=0,
                 at_depth_threshold=0.15):
        """
        :param data: the time and depth values for the dive
        :param columns: a dictionary of column mappings for the data
        :param surface_threshold: minmum depth to constitute a dive
        :param th_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        """

        if data[columns['time']].dtypes != np.float64:
            data.time = date2num(data.time.tolist(), units=units)

        self.data = data.sort_values('time').reset_index(drop=True)
        self.surface_threshold = surface_threshold

        for k, v in columns.items():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v, axis=1)

        self.max_depth = self.data.depth.max()
        self.dive_start = self.data.time.min()
        self.dive_end = self.data.time.max()
        self.bottom_start = None
        self.td_bottom_duration = None
        self.bottom_difference = None
        self.td_total_duration = self.dive_end - self.dive_start
        try:
            self.td_descent_duration = self.get_descent_duration(
                at_depth_threshold)
            self.td_ascent_duration = self.get_ascent_duration(
                at_depth_threshold)
            self.td_surface_duration = self.get_surface_duration()
            self.bottom_variance = self.set_bottom_variance()
            self.descent_velocity = self.get_descent_velocity()
            self.ascent_velocity = self.get_ascent_velocity()

            self.td_dive_duration = self.td_total_duration -    \
                self.td_surface_duration
            self.no_skew = 0
            self.right_skew = 0
            self.left_skew = 0
            self.set_skew()
            self.peaks = self.get_peaks(surface_threshold)
            self.insufficient_data = False
        except:
            self.insufficient_data = True

    def get_descent_duration(self, at_depth_threshold=0.15):
        """
        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        :return: the descent duration in seconds
        """
        std_dev = 0
        for i, r in self.data.iterrows():
            next_std_dev = np.std(self.data.loc[:i, 'depth'])
            if ((i + 1) not in self.data.index
                or (next_std_dev <= std_dev or self.data.loc[i, 'depth'] >=
                    self.data.loc[(i + 1), 'depth']
                    ) and self.data.loc[i, 'depth'] > (self.max_depth
                                                       * (1 - at_depth_threshold))):
                self.bottom_start = self.data.loc[i, 'time']
                return (self.data.loc[i, 'time'] - self.data.loc[0, 'time'])
                break
            else:
                std_dev = next_std_dev
        return self.td_descent_duration

    def get_ascent_duration(self, at_depth_threshold=0.15):
        """
        This function also sets the bottom duration.

        :param at_depth_threshold: a value from 0 - 1 indicating distance from
            the bottom of the dive at which the animal is considered to be at
            depth
        :return: the ascent duration in seconds
        """
        end_index = -1
        std_dev = 0

        # Find the crest of the dive in reversed values
        for i, r in self.data.sort_values('time', ascending=False).iterrows():
            if self.data.loc[(i - 1), 'depth'] > self.surface_threshold:
                end_index = i
                break

        # Finds the the change in standard deviation to determine the end of
        # the bottom of the divide.
        for i, r in self.data[:end_index].sort_values(
                'time', ascending=False).iterrows():
            next_std_dev = np.std(self.data.loc[i:end_index, 'depth'])
            if ((next_std_dev < std_dev or
                 self.data.loc[i, 'depth']
                 >= self.data.loc[(i - 1), 'depth']) and
                    self.data.loc[i, 'depth']
                    > (self.max_depth * (1 - at_depth_threshold))) or     \
                    self.data.loc[i, 'depth'] > (self.max_depth * 0.90):
                self.td_bottom_duration = self.data.loc[i, 'time'] -    \
                    self.bottom_start
                if (end_index > 0):
                    return (self.data.loc[end_index, 'time']
                            - self.data.loc[i, 'time'])

                break
            else:
                std_dev = next_std_dev
        return self.td_ascent_duration

    # Get the surface duration by subtracting the ascent, descent, and bottom
    # durations.
    def get_surface_duration(self):
        """
        :return: the surface duration in seconds
        """
        duration = self.data.time.max() - self.data.time.min()
        self.td_surface_duration = duration - self.td_descent_duration - \
            self.td_bottom_duration - self.td_ascent_duration
        return self.td_surface_duration

    # Calculate the descent velocity Delta Depth/Delta Time
    def get_descent_velocity(self):
        """
        :return: the descent velocity in m/s
        """
        self.descent_velocity = 0
        descent_data = self.data[self.data.time <= self.bottom_start]
        if self.td_descent_duration > 0:
            self.descent_velocity = (
                descent_data.depth.max()
                - descent_data.depth.min()) / self.td_descent_duration
        return self.descent_velocity

    # Calculate the ascent velocity Delta Depth/Delta Time
    def get_ascent_velocity(self):
        """
        :return: the ascent velocity in m/s
        """
        self.ascent_velocity = 0
        ascent_data = self.data[
            (self.data.time
             >= (self.bottom_start + self.td_bottom_duration))
            & (self.data.time
               <= (self.data.time.max() - self.td_surface_duration))
        ]
        self.ascent_velocity = (
            ascent_data.depth.max()
            - ascent_data.depth.min()) / self.td_ascent_duration
        return self.ascent_velocity

    # Calculate and set the bottom variance
    def set_bottom_variance(self):
        """
        This function also set total dive variance

        :return: the standard variance in depth during the bottom portion of
            the dive in meters
        """
        dive_data = self.data[(self.data.time >= self.dive_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration
                               + self.td_ascent_duration))]
        self.dive_variance = np.std(dive_data.depth)
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration))]
        self.bottom_variance = np.std(bottom_data.depth)
        self.bottom_difference = bottom_data.depth.max(
        ) - bottom_data.depth.min()
        return self.bottom_variance

    # Calculate and set total dive variance
    def set_dive_variance(self):
        """
        :return: the standard variancet in depth during dive in meters
        """
        dive_data = self.data[(self.data.time >= self.dive_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration +
                               self.td_ascent_duration))]
        self.dive_variance = np.std(dive_data.depth)
        return self.dive_variance

    def set_skew(self):
        """
        Sets the objects skew as left, right, or no skew
        """
        if self.td_ascent_duration > self.td_descent_duration:
            self.right_skew = 1
        elif self.td_descent_duration > self.td_ascent_duration:
            self.left_skew = 1
        else:
            self.no_skew = 1

    def get_peaks(self, surface_threshold=0):
        """
        :return: number of peaks found within a dive
        """
        self.peaks = 0
        # Get and set the bottom data
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration))].reset_index()

        bottom_difference = (bottom_data.depth.max() - bottom_data.depth.min())

        if bottom_difference != 0:
            threshold = max((bottom_data.depth.std(
            ) / (bottom_data.depth.max() - bottom_data.depth.min())), 0.5)
        else:
            threshold = 0.5
        peaks = pk.indexes(
            bottom_data.depth * (-1),
            thres=threshold,
            min_dist=max((10 / self.data.time.diff().mean()), 3))

        peak_data = bottom_data[(bottom_data.index.isin(peaks)) & (
            bottom_data.depth > surface_threshold)]
        self.peaks = len(peak_data)
        return self.peaks

    # Return the dictionary of the object
    def to_dict(self):
        """
        :return: a dictionary of the dive profile
        """
        dive = copy.deepcopy(self.__dict__)
        del dive['data']
        return dive

    # Used to plot the dive
    def plot(self):
        """
        :return: a plotly graph showing the phases of the dive
        """
        # Get and set the descent data
        descent_data = self.data[self.data.time <= self.bottom_start]
        descent = go.Scatter(
            x=num2date(descent_data.time.tolist(), units=units),
            y=descent_data.depth,
            mode='lines+markers',
            name='Descent')

        # Get and set the bottom data
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration))]

        bottom = go.Scatter(
            x=num2date(bottom_data.time.tolist(), units=units),
            y=bottom_data.depth,
            mode='lines+markers',
            name='Bottom')

        # Get and set the ascent data
        ascent_data = self.data[
            (self.data.time
             >= (self.bottom_start + self.td_bottom_duration))
            & (self.data.time
               <= (self.data.time.max() - self.td_surface_duration))
        ]
        ascent = go.Scatter(
            x=num2date(ascent_data.time.tolist(), units=units),
            y=ascent_data.depth,
            mode='lines+markers',
            name='Ascent')

        # Get and set the surface data
        surface_data = self.data[self.data.time >= (
            self.data.time.max() - self.td_surface_duration)]

        surface = go.Scatter(
            x=num2date(surface_data.time.tolist(), units=units),
            y=surface_data.depth,
            mode='lines+markers',
            name='Surface')

        layout = go.Layout(
            title='Dive starting at {}'.format(
                num2date(self.dive_start, units=units)),
            xaxis=dict(title='Time'),
            yaxis=dict(title='Depth in Meters', autorange='reversed'))
        plot_data = [descent, bottom, ascent, surface]
        fig = go.Figure(data=plot_data, layout=layout)
        return py.iplot(fig)
