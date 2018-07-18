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
            data.time = num2date(data.time.tolist(),units=units)

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
        self.average_vertical_velocity = np.absolute(((dive.depth.diff()/dive.time.diff()))).mean()
        self.average_descent_velocity = self.get_average_descent_velocity()
        self.average_ascent_velocity = self.get_average_ascent_velocity()
        self.number_of_descent_transitions = len(self.data[(self.data.depth.diff()/self.data.time.diff()) > 0])
        self.number_of_ascent_transitions = len(self.data[(self.data.depth.diff()/self.data.time.diff()) > 0])
        self.total_descent_distance_travelled = self.get_descent_vertical_distance()
        self.total_ascent_distance_travelled = self.get_ascent_vertical_distance()
        self.peaks = self.get_peaks()
        self.overall_change_in_depth =  self.data.depth.diff().sum()
        self.time_at_depth = self.get_time_at_depth()

    def get_peaks(self):
        """
        :return: number of peaks found within a dive
        """
        peak_thres = (1 - (dive.depth.min()/ dive.depth.max()))
        peaks = pk.indexes(self.data.depth*(-1), thres=min([0.2, peak_thres]), min_dist=max((10/self.data.time.diff().mean()),3))
        self.peaks = len(peaks)
        return self.peaks

    def get_time_at_depth(self):
        dive = self.data.copy(deep=True)
        dive['time_diff']= dive.time.diff()
        time = dive[dive.depth > (dive.depth.max() - ((dive.depth.max() - dive.depth.min()) * 0.15))].time_diff.sum()
        del dive
        return time.total_seconds()

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
        velocity = np.absolute(dive[dive.velocity < 0].velocity.mean())
        del dive
        return velocity

    def get_average_descent_velocity(self):
        dive = self.data.copy(deep=True)
        velocity = np.absolute(dive[dive.velocity > 0].velocity.mean())
        del dive
        return velocity
