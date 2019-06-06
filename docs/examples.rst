.. _examples_page:

=============
Code Examples
=============

Divebomb
--------

The example data set below is dive data from grey seal over the course of a few days.

Example data set: :download:`Seal Dives <_static/seal_dive_data.csv>`

Dives
*****

Pass a Pandas DataFrame to the function with a ``time`` and a ``depth``
(in positive meters) column. Provide the surface threshold using
``surface_threshold`` (in meters). Refine other arguments as needed.

.. code:: python

  from divebomb import profile_cluster_export
  import pandas as pd

  data = pd.read_csv('/path/to/data.csv')
  surface_threshold=3

  profile_cluster_export(data, folder='results', surface_threshold=surface_threshold , columns={'depth': 'depth', 'time': 'time'})


DeepDives
*********

To run the ``profile_cluster_export()`` function on an animal, such as a shark, just set
``is_surfacing_animal==False``. This variable makes the function call the
``DeepDive`` class instead. ``DeepDives`` are not dependent on the animal
surfacing again.

.. code:: python

  import pandas as pd
  from divebomb import profile_cluster_export

  df = pd.read_csv('/path/to/data.csv')

  dives = profile_cluster_export(df, folder='results', is_surfacing_animal=False)

Changing Surface threshold
**************************

A surface threshold is used for surfacing animals to define a depth window for
what is considered to be at surface. The ``surface_threshold`` argument
defaults to ``0`` but can be changed in the ``profile_cluster_export()`` function.
For example ``surface_threshold=2`` might be passed for animal that is ``~2``
meters long. ``surface_threshold`` is always passed in meters.


Example:

.. code:: python

  import pandas as pd
  from divebomb import profile_cluster_export

  data = pd.read_csv('data.csv')

  surface_threshold = 3 # in meters

  dives = profile_cluster_export(data, folder='results', surface_threshold=surface_threshold)

Changing At Depth Threshold
***************************

An at depth threshold is used in both the ``Dive`` and the ``DeepDive`` class.
The ``at_depth_thresold`` argument is a value between ``0`` and ``1`` that
determines the window for when an animal is considered to be at bottom of its
dive. The default value is ``0.15`` which means the bottom ``15%`` of the
relative depth is considered to be at bottom. ``at_depth_thresold`` is always
as value between ``0`` and ``1`` expressing a percentage.


Example:

.. code:: python

  import pandas as pd
  from divebomb import profile_cluster_export

  data = pd.read_csv('data.csv')

  at_depth_threshold = 0.2 # A value betwen 0 and 1

  dives = profile_cluster_export(data, folder='results', minimal_time_between_dives=minimal_time_between_dives)

Changing Dive Detection Sensitivity
***********************************

The ``dive_detection_sensitivity`` argument is a value between ``0`` and ``1``.
The default is ``0.98`` for surfacing animals and ``0.5`` for non-surfacing
animals. The ``dive_detection_sensitivity`` helps determine range where dive
starts can be determined.


Example:

.. code:: python

  import pandas as pd
  from divebomb import profile_cluster_export

  data = pd.read_csv('data.csv')

  dive_detection_sensitivity = 0.95

  dives = profile_cluster_export(data, folder='results', dive_detection_sensitivity=dive_detection_sensitivity)

Changing Minimal Time Between Dives
***********************************

The ``minimal_time_between_dives`` is the minimum time (in seconds) that has
to occur before a new dive can start. The default value for this is ``10``
seconds.


Example:

.. code:: python

  import pandas as pd
  from divebomb import profile_cluster_export

  data = pd.read_csv('data.csv')

  minimal_time_between_dives = 600 # in seconds

  dives = profile_cluster_export(data, folder='results', minimal_time_between_dives=minimal_time_between_dives)


Separating Out Components
-------------------------

Each of the components from `profile_cluster_export()` can run separately but their input
may rely on the out put from the previous. Below is how to run each of the components separately
to modify the clustering or export to CSVs



Profile Dives
*************

The ``profile_dives()`` function only profiles the dives. It finds the start points for the
dives, then finds the dive attributes. ``profile_dives()`` takes the ``surface_threshold``,
``dive_detection_sensitivity``, ``at_depth_thresold``, and ``is_surfacing_animal`` arguments
just like ``profile_cluster_export()``. It returns three datasets of the profiled dives, any
insufficient dives, and the original data.

.. code:: python

  from divebomb import profile_dives
  import pandas as pd

  data = pd.read_csv('/path/to/data.csv')
  surface_threshold=3

  dives, insufficient_dives, data = profile_dives(data, surface_threshold=surface_threshold)

``profile_dives()`` also takes and argument to display the dive in a Jupyter Notebook.
If ``ipython_display_mode=True`` then the dives will be displayed with with a slider to
choose the dive.

.. code:: python

  from divebomb import profile_dives
  import pandas as pd

  data = pd.read_csv('/path/to/data.csv')
  surface_threshold=3

  profile_dives(data, surface_threshold=surface_threshold, ipython_display_mode=True)



Cluster Dives
*************

Export Dives
************

Dives can either be exported to NetCDF or CSV. Both ``profile_dives()`` and ``cluster_dives()``
need to be run and assigned to variables to get all dataset created in the process.

Plotting Results
----------------

Divebomb includes two functions to plot dives. The first, ``plot_from_nc()``
will plot a single dive with disinguished phases. ``plot_from_nc()`` includes a
``type`` argument that can either be ``dive`` or ``deepdive``.

The second function ``cluster_summary_plot`` will plot the minimum, maximum,
and mean depth for each cluster. Time is asjusted to be the number of seconds
into the dive, rather than a timestamp. Both axes can be individually scaled
relative to maximum values of the clusters. For example, time can be scaled to
be a proigress percentage through the dive. Scaling can be applied by passing
the following: ``scale={'depth'=True, 'time':True}`` Below are examples and how
they can be applied.

Single Dive
***********

Below is an example of a single dive from a surfacing animal.

.. code:: python

  from divebomb.plotting import plot_from_nc, cluster_summary_plot

  path = '/path/to/results_folder'
  cluster = 2
  dive_id = 555

  # Plot inside a notebook
  plot_from_nc(path, cluster, dive_id, ipython_display=True)

  # Plot out to an HTML file
  plot_from_nc(path, cluster, dive_id, ipython_display=False, filename="dive.html")

.. raw:: html

  <iframe src="_static/single_dive.html" height="400px" width="100%"></iframe><hr/>




Dive Clusters
*************

Below is an example of the clusters from a surfacing animal.

.. code:: python

  from divebomb.plotting import cluster_summary_plot

  path = '/path/to/results_folder'

  # Plot inside a notebook
  cluster_summary_plot(path, ipython_display=True)

  # Plot out to an HTML file
  cluster_summary_plot(path, ipython_display=False, filename="clusters.html", scale={'depth':False, 'time':True})

.. raw:: html

  <iframe src="_static/surface_clusters.html" height="400px" width="100%"></iframe><hr/>




Single DeepDive
***************

Below is an example of non-surfacing animal dive. This example is also a
sparser dataset as there are 10 minutes between data points.

.. code:: python

  from divebomb.plotting import plot_from_nc, cluster_summary_plot

  path = '/path/to/results_folder'
  cluster = 3
  dive_id = 68

  # Plot inside a notebook
  plot_from_nc(path, cluster, dive_id, ipython_display=True, type='deepdive)

  # Plot out to an HTML file
  plot_from_nc(path, cluster, dive_id, ipython_display=False, filename='single_deepdive.html', type='deepdive')

.. raw:: html

  <iframe src="_static/single_deepdive.html" height="400px" width="100%"></iframe><hr/>




Clustered DeepDives
*******************

Below is an example of the clusters from a non-surfacing animal. This example
is also a sparser dataset as there are 10 minutes between data points.

.. code:: python

  from divebomb.plotting import cluster_summary_plot

  path = '/path/to/results_folder'

  # Plot inside a notebook
  cluster_summary_plot(path, ipython_display=True)

  # Plot out to an HTML file
  cluster_summary_plot(path, ipython_display=False, filename='deepdive_clusters.html', title='DeepDive Clusters')

.. raw:: html

  <iframe src="_static/deepdive_clusters.html" height="400px" width="100%"></iframe>


Correcting Depth on  Surfacing Animals
--------------------------------------

Depth recordings can be uncalihrated or drift over time. The following are two ways from divebomb's
:ref:`preprocessing module <preprocessing_functions_page>` to correct for the offset on a **surfacing animal**.
The data passes to the function must have ``time`` and a ``depth`` (in positive meters) columns.
The first uses a local max:

.. code:: python

  from divebomb import profile_cluster_export
  import pandas as pd
  window = 3600 #seconds

  data = pd.read_csv('/path/to/data.csv')
  corrected_depth_data = correct_depth_offset(data, window=window, aux_file='results/aux_file.nc')

The second wethod uses a rolling average of all surface and near surface values in the time window:

.. code:: python

  from divebomb import profile_cluster_export
  import pandas as pd
  window = 3600 # seconds
  surface_threshold = 4 # meters

  data = pd.read_csv('/path/to/data.csv')
  corrected_depth_data = correct_depth_offset(data, window=window, method='mean', surface_threshold=surface_threshold, aux_file='results/aux_file.nc')
