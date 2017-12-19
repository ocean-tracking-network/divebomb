Divebomb
========
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
  - **dive_variance** - the variance in depth for the entire dive.
  - **descent_velocity** - the average velocity of the descent.
  - **ascent_velocity** the average velocity of the descent.
  - **dive_shape** - the text classification of the dive using the DiveShape enumeration.
  - **skew** - the text classification of the dive using the DiveShape enumeration.
  - **bottom_shape** - the text classification of the dive using the DiveShape enumeration.

The dives are then display through iPython notebooks or saved to CSV files.
