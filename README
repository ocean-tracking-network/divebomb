Divebomb
==========
Divebomb is a python package that uses pandas to divide a timeseries of depths into idividual dives.

Each dive is then profiled with the following attributes: 
- **max_depth** - the max depth in the dive
- **dive_start** - the timestamp of the first point in the dive.
- **bottom_start** - the timestamp of the first point in the dive when the animal is at depth.
- **td_bottom_duration** - a timedelta object containing the duration of the time the animal is at depth in seconds.
- **td_descent_duration** - a timedelta object containing the duration of the time the animal is descending in seconds.
- **td_ascent_duration** - a timedelta object containing the duration of the time the animal is ascending in seconds.
- **td_surface_duration** - a timedelta object containing the duration of the time the animal is at the surface in seconds.
- **bottom_variance** - the variance of the depth while the animal is at the bottom of the dive.
- **descent_velocity** - the average velocity of the descent.
- **ascent_velocity** the average velocity of the descent.
- **shape** - the text classification of the dive using the DiveShape enumeration.

The dives are then display through iPython notebooks or saved to CSV files.

Implementation
--------------
1. Determine the starting point of each dive by passing a Pandas DataFrame to *profile_dives()* and replace the deault vales as necessary
    ```python
    profile_dives(data, folder=None, columns={'depth': 'depth', 'time': 'time'}, acceleration_threshold=0.015, surface_threshold=3.0, ipython_display_mode=False)
    ```

2. Pull the descent, bottom, ascent, and surface attributes from the dive profile. Calling dive on the individual dive data with column mappings and a surface thrshold
```python
Dive(self, data, columns={'depth': 'depth', 'time': 'time'}, surface_threshold=3.0)
```
3. Use the attributes from the previous step and the thresholds to classify the shape of the dive
```python
Dive.set_dive_shape(self, minimum_skew_ratio=2, v_threshold=0.1, min_variance=0.5)
```
4. The dive data is displayed to the user or stored in files
```python
#Display
profile_dives(df, ipython_display_mode=True)
#Store in files
profile_dives(df, 'result')
```