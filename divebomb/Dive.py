'''
Dive
----
'''


from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
import copy
import sys
from DiveShape import DiveShape
from netCDF4 import Dataset, num2date, date2num

units = 'seconds since 1970-01-01'

class Dive:
    # Durations are in seconds and velocity in m/s
    def __init__(self, data, columns={'depth': 'depth', 'time': 'time'}, surface_threshold=3.0):
        self.sufficient=True
        if data[columns['time']].dtypes != np.float64:
            data.time = num2date(data.time.tolist(),units=units)

        self.data = data.sort_values('time').reset_index(drop=True)
        self.surface_threshold = surface_threshold

        for k, v in columns.iteritems():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v, axis=1)
        self.max_depth = self.data.depth.max()
        self.dive_start = self.data.time.min()
        self.bottom_start = None
        self.td_bottom_duration = None
        try:
            self.td_descent_duration = self.get_descent_duration()
            self.td_ascent_duration = self.get_ascent_duration()
            self.td_surface_duration = self.get_surface_duration()
            self.bottom_variance = self.set_bottom_variance()
            self.descent_velocity = self.get_descent_velocity()
            self.ascent_velocity = self.get_ascent_velocity()
            self.shape = self.set_dive_shape()

        except Exception:
            self.sufficient=False
            if self.data.depth.max() <= surface_threshold:
                self.td_descent_duration = None
                self.td_ascent_duration = None
                self.td_surface_duration = None
                self.bottom_variance = None
                self.descent_velocity = None
                self.ascent_velocity = None
                self.shape = DiveShape.SHALLOW
            else:
                print "Error: There is not enough information for this dive.\n"+str(self.data.time.min() )+ " to "+str(self.data.time.max())
    # Calculate and set the descent duration
    def get_descent_duration(self):
        std_dev = 0
        for i, r in self.data.iterrows():
            next_std_dev = np.std(self.data.loc[:i, 'depth'])
            if (next_std_dev <= std_dev or self.data.loc[i, 'depth'] >= self.data.loc[(i + 1), 'depth']) and self.data.loc[i, 'depth'] > (self.max_depth * 0.8):
                self.bottom_start = self.data.loc[i, 'time']
                return (self.data.loc[i, 'time'] - self.data.loc[0, 'time'])
                break
            else:
                std_dev = next_std_dev
        return self.td_descent_duration

    # Calculate and set the ascent duration
    def get_ascent_duration(self):
        end_index = -1
        std_dev = 0
        for i, r in self.data.sort_values('time', ascending=False).iterrows():

            if self.data.loc[(i - 1), 'depth'] > self.surface_threshold:
                end_index = i
                break

        for i, r in self.data.sort_values('time', ascending=False)[:end_index].iterrows():

            next_std_dev = np.std(self.data.loc[i:end_index, 'depth'])
            if (next_std_dev < std_dev or self.data.loc[i, 'depth'] >= self.data.loc[(i - 1), 'depth']) and self.data.loc[i, 'depth'] > (self.max_depth * 0.85):
                self.td_bottom_duration = self.data.loc[i,'time'] - self.bottom_start
                if(end_index > 0):
                    return (self.data.loc[end_index, 'time'] - self.data.loc[i, 'time'])
                break
            else:
                std_dev = next_std_dev
        return self.td_ascent_duration


    # Calculate and set the descent duration
    def get_surface_duration(self):
        duration = self.data.time.max() - self.data.time.min()
        self.td_surface_duration = duration - self.td_descent_duration - \
            self.td_bottom_duration - self.td_ascent_duration
        return self.td_surface_duration

    # Calculate the ascent velocity
    def get_descent_velocity(self):
        descent_data = self.data[self.data.time <= self.bottom_start]
        self.descent_velocity = (descent_data.depth.max(
        ) - descent_data.depth.min()) / self.td_descent_duration
        return self.descent_velocity

    # Calculate the ascent velocity
    def get_ascent_velocity(self):
        ascent_data = self.data[self.data.time >= (
            self.bottom_start + self.td_bottom_duration)]
        self.ascent_velocity = (ascent_data.depth.max() - ascent_data.depth.min()) / self.td_ascent_duration
        return self.ascent_velocity

    # Calculate and set the bottom variance
    def set_bottom_variance(self):
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (
            self.data.time <= (self.bottom_start + self.td_bottom_duration))]
        self.bottom_variance = np.std(bottom_data.depth)
        return self.bottom_variance

    # Calculate and set the descent duration
    def set_dive_shape(self, minimum_skew_ratio=2, v_threshold=0.1, min_variance=0.5):
        shape = ""
        total_duration = self.td_descent_duration + \
            self.td_bottom_duration + self.td_ascent_duration

        if self.td_ascent_duration > self.td_descent_duration * minimum_skew_ratio:
            shape += str(DiveShape.RIGHTSKEW)
            shape += " - "
        elif self.td_descent_duration > self.td_ascent_duration * minimum_skew_ratio:
            shape += str(DiveShape.LEFTSKEW)
            shape += " - "

        if self.td_bottom_duration <= total_duration * v_threshold:
            shape += str(DiveShape.VSHAPE)
            shape += " - "
        else:
            shape += str(DiveShape.SQUARE)
            shape += " - "

        if self.bottom_variance > min_variance:
            shape += str(DiveShape.WIGGLE)
        else:
            shape += str(DiveShape.FLAT)

        self.shape = shape
        return self.shape

    def to_dict(self):
        dive = copy.deepcopy(self.__dict__)
        del dive['data']
        return dive

    def plot(self):
        if self.sufficient and self.shape != DiveShape.SHALLOW:
            descent_data = self.data[self.data.time <= self.bottom_start]
            descent = go.Scatter(
                x=num2date(descent_data.time.tolist(), units=units),
                y=descent_data.depth,
                mode='lines+markers',
                name='Descent'
            )

            bottom_data = self.data[(self.data.time >= self.bottom_start) & (
                self.data.time <= (self.bottom_start + self.td_bottom_duration))]
            bottom = go.Scatter(
                x=num2date(bottom_data.time.tolist(), units=units),
                y=bottom_data.depth,
                mode='lines+markers',
                name='Bottom'
            )

            ascent_data = self.data[(self.data.time >= (self.bottom_start + self.td_bottom_duration)) & (
                self.data.time <= (self.data.time.max() - self.td_surface_duration))]
            ascent = go.Scatter(
                x=num2date(ascent_data.time.tolist(), units=units),
                y=ascent_data.depth,
                mode='lines+markers',
                name='Ascent'
            )

            surface_data = self.data[self.data.time >= (
                self.data.time.max() - self.td_surface_duration)]

            surface = go.Scatter(
                x=num2date(surface_data.time.tolist(), units=units),
                y=surface_data.depth,
                mode='lines+markers',
                name='Surface'
            )

            layout = go.Layout(title=self.shape,xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))

            plot_data = [descent, bottom, ascent, surface]

            fig = go.Figure(data=plot_data, layout=layout)
            return py.iplot(fig)

        elif self.shape == DiveShape.SHALLOW:
            dive= go.Scatter(
                x=num2date(self.data.time.tolist(), units=units),
                y=self.data.depth,
                mode='lines+markers',
                name='Dive'
            )

            layout = go.Layout(title=str(self.shape),xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))

            plot_data = [dive]

            fig = go.Figure(data=plot_data, layout=layout)
            return py.iplot(fig)
        else:
            print "Insufficient data to plot."
