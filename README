Divebomb
--------

Divebomb is a python package that uses pandas to divide a timeseries of depths into individual dives. The dives are profiled as a ``Dive`` or ``DeepDive``
depending on the animal. The ``Dive`` class is used for frequently surfacing animals, such as seals and whales. The ``DeepDive`` class is used for  infrequently surfaceing animals, like sharks.

The dive profiles are reduced to 8 dimensions using Principal Component Analsysis. Guassian Mixed Models are generated using theses variables
and the minimal Bayesian Information Criterion is used to determine the optimal number of clusters. The dives are split into the clusters using
Agglomerative Hierarchical Clustering (from sklearn). The dives are then display through iPython notebooks or saved to netCDF files organized by cluster.

Documentation
-------------

The official documentation is hosted on here: http://divebomb.readthedocs.io/en/latest/

Dive
****

A ``Dive`` is then profiled with the following attributes:

- ``max_depth`` - the max depth in the dive
- ``dive_start`` - the timestamp of the first point in the dive
- ``dive_end`` - the timestamp of the last point in the dive
- ``bottom_start`` - the timestamp of the first point in the dive when the animal is at depth
- ``td_bottom_duration`` - a timedelta object containing the duration of the time the animal is at depth in seconds
- ``td_descent_duration`` - a timedelta object containing the duration of the time the animal is descending in seconds
- ``td_ascent_duration`` - a timedelta object containing the duration of the time the animal is ascending in seconds
- ``td_surface_duration`` - a timedelta object containing the duration of the time the animal is at the surface in seconds
- ``bottom_variance`` - the variance of the depth while the animal is at the bottom of the dive
- ``dive_variance`` - the variance of the depth for the entire dive.
- ``descent_velocity`` - the average velocity of the descent
- ``ascent_velocity`` - the average velocity of the descent
- ``peaks`` - the number of peaks found in the dive profile
- ``left_skew`` - a boolean of 1 or 0 indicating if the dive is left skewed
- ``right_skew`` - a boolean of 1 or 0 indicating if the dive is right skewed
- ``no_skew`` - a boolean of 1 or 0 indicating if the dive is not skewed

DeepDive
********

A ``DeepDive`` is then profiled with the following attributes:

- ``max_depth`` - the max depth in the dive
- ``min_depth`` - the max depth in the dive
- ``dive_start`` - the timestamp of the first point in the dive
- ``dive_end`` - the timestamp of the last point in the dive
- ``td_total_duration`` - a timedelta (in seconds since 1970-01-01) containing the duration of the dive
- ``depth_variance`` - the variance of the depth for the entire dive.
- ``average_vertical_velocity`` - the mean velocity of the animal over the entire dive with negative value indicating upward movement
- ``average_descent_velocity`` - the average velocity of any downward movement as positive value
- ``average_ascent_velocity`` - the average velocity of any upward movement as positive value
- ``number_of_descent_transitions`` - the number of times and animal moves descends any distance in the dive period
- ``number_of_ascent_transitions`` - the number of times and animal moves ascends any distance in the dive period
- ``total_descent_distance_traveled`` - the total absolute distance in meters in which the anaimal moves down
- ``total_ascent_distance_traveled`` - the total absolute distance in meters in which the anaimal moves up
- ``overall_change_in_depth`` - the difference between the minimum and maximum depth within the dive period
- ``td_time_at_depth`` - the duration in seconds at which the animal spends in the deepest part of the vertical movement (< 85% depth)
- ``td_time_pre_depth`` - the duration in seconds befor the deepest part of the vertical movement (< 85% depth)
- ``td_time_post_depth`` - the duration in seconds after the deepest part of the vertical movement (< 85% depth)
- ``peaks`` - the number of peaks found in the dive profile
- ``left_skew`` - a boolean of 1 or 0 indicating if the dive is left skewed
- ``right_skew`` - a boolean of 1 or 0 indicating if the dive is right skewed
- ``no_skew`` - a boolean of 1 or 0 indicating if the dive is not skewed

Surface Thresholds
******************

A surface threshold is used for surfacing animals to define a depth window for what is considered to be at surface. The ``surface_threshold`` argument defaults to ``0`` but can be changed in the ``profile_dives()`` function. For example ``surface_threshold=2`` might be passed for animal that is ``~2`` meters long. ``surface_threshold`` is always passed in meters.

At Depth Thresholds
*******************

An at depth threshold is used in bothe the ``Dive`` and the ``DeepDive`` class. The ``at_depth_thresold`` argument is a value between ``0`` and ``1`` that determines the window for when an animal is considered to be at bottom of its dive. The default value is ``0.15`` which means the bottom ``15%`` of the relative depth is considered to be at bottom. ``at_depth_thresold`` is always as value between ``0`` and ``1`` expressing a percentage.

Skews
*****

A skew is defined as any difference one way or the other in descent or ascent times for the ``Dive`` class and any difference in pre-depth or post-depth time for a ``DeepDive``. This method was chosen as researchers found skew was most accurately represented when any difference between the values existed.

Timestamps
**********

The input timestamps are expected to be in a datetime format. The output timestamps are in ``seconds since 1970-01-01``.
Every netCDF file has the time unit saved as an attribute as a reminder. All dive attributes that start with ``td_`` are
a duration in seconds. The ``time``, ``dive_start``, ``dive_end``, and ``bottom_start`` will use the units mentioned above.
the netCDF4 library has a ``num2date`` function that will convert the values back to a datetime object.

Divebomb
--------

Divebomb is a python package that uses pandas to divide a timeseries of depths into individual dives. The dives are profiled as a ``Dive`` or ``DeepDive``
depending on the animal. The ``Dive`` class is used for frequently surfacing animals, such as seals and whales. The ``DeepDive`` class is used for  infrequently surfaceing animals, like sharks.

The dive profiles are reduced to 8 dimensions using Principal Component Analsysis. Guassian Mixed Models are generated using theses variables
and the minimal Bayesian Information Criterion is used to determine the optimal number of clusters. The dives are split into the clusters using
Agglomerative Hierarchical Clustering (from sklearn). The dives are then display through iPython notebooks or saved to netCDF files organized by cluster.


Dive
****

A ``Dive`` is then profiled with the following attributes:

- ``max_depth`` - the max depth in the dive
- ``dive_start`` - the timestamp of the first point in the dive
- ``dive_end`` - the timestamp of the last point in the dive
- ``bottom_start`` - the timestamp of the first point in the dive when the animal is at depth
- ``td_bottom_duration`` - a timedelta object containing the duration of the time the animal is at depth in seconds
- ``td_descent_duration`` - a timedelta object containing the duration of the time the animal is descending in seconds
- ``td_ascent_duration`` - a timedelta object containing the duration of the time the animal is ascending in seconds
- ``td_surface_duration`` - a timedelta object containing the duration of the time the animal is at the surface in seconds
- ``bottom_variance`` - the variance of the depth while the animal is at the bottom of the dive
- ``dive_variance`` - the variance of the depth for the entire dive.
- ``descent_velocity`` - the average velocity of the descent
- ``ascent_velocity`` - the average velocity of the descent
- ``peaks`` - the number of peaks found in the dive profile
- ``left_skew`` - a boolean of 1 or 0 indicating if the dive is left skewed
- ``right_skew`` - a boolean of 1 or 0 indicating if the dive is right skewed
- ``no_skew`` - a boolean of 1 or 0 indicating if the dive is not skewed


DeepDive
********

A ``DeepDive`` is then profiled with the following attributes:

- ``max_depth`` - the max depth in the dive
- ``min_depth`` - the max depth in the dive
- ``dive_start`` - the timestamp of the first point in the dive
- ``dive_end`` - the timestamp of the last point in the dive
- ``td_total_duration`` - a timedelta (in seconds since 1970-01-01) containing the duration of the dive
- ``depth_variance`` - the variance of the depth for the entire dive.
- ``average_vertical_velocity`` - the mean velocity of the animal over the entire dive with negative value indicating upward movement
- ``average_descent_velocity`` - the average velocity of any downward movement as positive value
- ``average_ascent_velocity`` - the average velocity of any upward movement as positive value
- ``number_of_descent_transitions`` - the number of times and animal moves descends any distance in the dive period
- ``number_of_ascent_transitions`` - the number of times and animal moves ascends any distance in the dive period
- ``total_descent_distance_traveled`` - the total absolute distance in meters in which the anaimal moves down
- ``total_ascent_distance_traveled`` - the total absolute distance in meters in which the anaimal moves up
- ``overall_change_in_depth`` - the difference between the minimum and maximum depth within the dive period
- ``td_time_at_depth`` - the duration in seconds at which the animal spends in the deepest part of the vertical movement (< 85% depth)
- ``td_time_pre_depth`` - the duration in seconds befor the deepest part of the vertical movement (< 85% depth)
- ``td_time_post_depth`` - the duration in seconds after the deepest part of the vertical movement (< 85% depth)
- ``peaks`` - the number of peaks found in the dive profile
- ``left_skew`` - a boolean of 1 or 0 indicating if the dive is left skewed
- ``right_skew`` - a boolean of 1 or 0 indicating if the dive is right skewed
- ``no_skew`` - a boolean of 1 or 0 indicating if the dive is not skewed


Surface Thresholds
******************

A surface threshold is used for surfacing animals to define a depth window for what is considered to be at surface. The ``surface_threshold`` argument defaults to ``0`` but can be changed in the ``profile_dives()`` function. For example ``surface_threshold=2`` might be passed for animal that is ``~2`` meters long. ``surface_threshold`` is always passed in meters.


At Depth Thresholds
*******************

An at depth threshold is used in bothe the ``Dive`` and the ``DeepDive`` class. The ``at_depth_thresold`` argument is a value between ``0`` and ``1`` that determines the window for when an animal is considered to be at bottom of its dive. The default value is ``0.15`` which means the bottom ``15%`` of the relative depth is considered to be at bottom. ``at_depth_thresold`` is always as value between ``0`` and ``1`` expressing a percentage.


Skews
*****

A skew is defined as any difference one way or the other in descent or ascent times for the ``Dive`` class and any difference in pre-depth or post-depth time for a ``DeepDive``. This method was chosen as researchers found skew was most accurately represented when any difference between the values existed.


Timestamps
**********

The input timestamps are expected to be in a datetime format. The output timestamps are in ``seconds since 1970-01-01``.
Every netCDF file has the time unit saved as an attribute as a reminder. All dive attributes that start with ``td_`` are
a duration in seconds. The ``time``, ``dive_start``, ``dive_end``, and ``bottom_start`` will use the units mentioned above.
the netCDF4 library has a ``num2date`` function that will convert the values back to a datetime object.
