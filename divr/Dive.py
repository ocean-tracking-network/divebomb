from datetime import datetime,timedelta
import pandas as pd
import numpy as np

class Dive:
    # Durations are in seconds and velocity in m/s
    def __init__(self, data, columns={'lat':'lat', 'lon':'lon', 'depth':'depth', 'time':'time'}):
        data = pd.DataFrame()
        data['time'] = data[columns['time']]
        data['depth'] = data[columns['depth']]
        data['lat'] = data[columns['lat']]
        data['lon'] = data[columns['lon']]
        dt_start = datetime.strptime(data.time.min(), '%Y-%m-%d %H:%M:%S')
        dt_end = datetime.strptime(data.time.max(), '%Y-%m-%d %H:%M:%S')
        td_descent_duration = None
        td_bottom_duration = None
        td_ascent_duration= None
        td_surface_duration = None
        descent_velocity = None
        ascent_velocity = None
        dt_bottom_start = None
        bottom_variance = None
        shape = None

    # Calculate and set the descent duration
    def set_descent_duration(self):
        return self.td_descent_duration

    # Calculate and set the descent duration
    def set_bottom_duration(self):
        return self.td_bottom_duration

    # Calculate and set the ascent duration
    def set_ascent_duration(self):
        return self.td_ascent_duration

    # Calculate and set the descent duration
    def set_surface_duration(self):
        return self.td_surface_duration

    # Calculate the ascent velocity
    def set_descent_velocity(self):
        return self.descent_velocity

    # Calculate the ascent velocity
    def set_ascent_velocity(self):
        return self.ascent_velocity

    # Calculate and set the descent duration
    def set_bottom_start(self):
        return self.td_bottom_start

    # Calculate and set the bottom variance
    def set_bottom_variance(self):
        return self.td_bottom_start

    # Calculate and set the descent duration
    def set_dive_shape(self, minimum_skew_ratio = 2):
        return self.shape
