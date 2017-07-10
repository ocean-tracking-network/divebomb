from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
py.init_notebook_mode()

class Dive:
    # Durations are in seconds and velocity in m/s
    def __init__(self, data, columns={'depth':'depth', 'time':'time'}, surface_threshold=2):
        self.data = data.sort_values('time').reset_index(drop=True)
        self.surface_threshold = surface_threshold

        for k,v in columns.iteritems():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v,axis=1)
        self.max_depth = self.data.depth.max()
        self.bottom_start = None
        self.td_bottom_duration = None
        self.td_descent_duration = self.get_descent_duration()
        self.td_ascent_duration= self.get_ascent_duration()
        self.td_surface_duration = self.get_surface_duration()
        self.bottom_variance = self.set_bottom_variance()
        self.descent_velocity = None
        self.ascent_velocity = None

        self.shape = None

    # Calculate and set the descent duration
    def get_descent_duration(self):
        std_dev = 0
        for i,r in self.data.iterrows():
            next_std_dev = np.std(self.data.loc[:i, 'depth'])
            if next_std_dev < std_dev or self.data.loc[i,'depth'] > self.data.loc[(i+1),'depth']:
                self.bottom_start = self.data.loc[i,'time']
                return (self.data.loc[i,'time'] - self.data.loc[0,'time'])
                break;
            else:
                std_dev = next_std_dev
        return self.td_descent_duration


    # Calculate and set the ascent duration
    def get_ascent_duration(self):
        end_index = -1
        std_dev = 0
        for i,r in  self.data.sort_values('time', ascending=False).iterrows():
            if self.data.loc[(i-1), 'depth'] > self.surface_threshold:
                end_index = i
                break;
        for i,r in  self.data.sort_values('time', ascending=False)[:end_index].iterrows():
            next_std_dev = np.std(self.data.loc[i:end_index, 'depth'])
            if (next_std_dev < std_dev or self.data.loc[i,'depth'] > self.data.loc[(i-1),'depth']) and self.data.loc[i,'depth'] > (self.max_depth*0.8):
                self.td_bottom_duration =  self.data.loc[i,'time']- self.bottom_start
                return (self.data.loc[end_index,'time'] - self.data.loc[i,'time'])
                break;
            else:
                std_dev = next_std_dev
        return self.td_ascent_duration

    # Calculate and set the descent duration
    def get_surface_duration(self):
        duration = self.data.time.max()-self.data.time.min()
        self.td_surface_duration = duration - self.td_descent_duration - self.td_bottom_duration - self.td_ascent_duration
        return self.td_surface_duration

    # Calculate the ascent velocity
    def set_descent_velocity(self):
        return self.descent_velocity

    # Calculate the ascent velocity
    def set_ascent_velocity(self):
        return self.ascent_velocity


    # Calculate and set the bottom variance
    def set_bottom_variance(self):
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (self.data.time <= (self.bottom_start+self.td_bottom_duration))]
        self.bottom_variance = np.std(bottom_data.depth)
        return self.bottom_variance

    # Calculate and set the descent duration
    def set_dive_shape(self, minimum_skew_ratio = 2):
        return self.shape

    def plot(self):
        descent_data = self.data[self.data.time <= self.bottom_start]
        descent = go.Scatter(
            x = descent_data.time,
            y = descent_data.depth,
            name = 'Descent'
        )

        bottom_data = self.data[(self.data.time >= self.bottom_start) & (self.data.time <= (self.bottom_start+self.td_bottom_duration))]
        bottom = go.Scatter(
            x = bottom_data.time,
            y = bottom_data.depth,
            name='Bottom'
        )

        ascent_data = self.data[self.data.time >= (self.bottom_start+self.td_bottom_duration)]
        ascent = go.Scatter(
            x = ascent_data.time,
            y = ascent_data.depth,
            name='Ascent'
        )

        surface_data = self.data[self.data.time >= (self.data.time.max() - self.td_surface_duration)]

        surface = go.Scatter(
            x = surface_data.time,
            y = surface_data.depth,
            name='Surface'
        )

        layout = go.Layout(yaxis=dict(autorange='reversed'))

        plot_data = [descent,bottom, ascent, surface]

        fig = go.Figure(data=plot_data, layout=layout)
        return  py.iplot(fig)
