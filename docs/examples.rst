.. _examples_page:

=============
Code Examples
=============

Divebomb
--------

Dives
*****

Pass a Pandas DataFrame to the function with a ``time`` and a ``depth`` (in positive meters) column. Provide the surface threshold using ``surface_threshold`` (in meters).
Refine other arguments as needed.

.. code:: python

  from divebomb import profile_dives
  import pandas as pd

  data = pd.read_csv('/path/to/data.csv')
  surface_threshold=3

  profile_dives(data, folder='results', surface_threshold=surface_threshold , columns={'depth': 'depth', 'time': 'time'}, ipython_display_mode=False)


The dive data can either be displayed to the user in Jupyter Notebooks or stored in files. Displaying will not
cluster the dives, but show them in ascending order by time in an iPython Notebook.

.. code:: python

  # Display
  surface_threshold = 3 # in meters
  profile_dives(df,  surface_threshold=surface_threshold , ipython_display_mode=True)

  # Store in files
  profile_dives(df, folder='results', surface_threshold=surface_threshold )

DeepDives
*********


Plotting Results
----------------

Divebomb includes two functions to plot dives. The first, ``plot_from_nc()``
will plot a single dive with disinguished phases.

Single Dive
***********

.. code:: python

  from divebomb.plotting import plot_from_nc, cluster_summary_plot

  path = '/path/to/results_folder'
  cluster = 4
  dive_id = 254

  # Plot inside a notebook
  plot_from_nc(path, cluster, dive_id, ipython_display=True)

  # Plot out to an HTML file
  plot_from_nc(path, cluster, dive_id, ipython_display=False, filename="dive.html")

.. raw:: html

  <iframe src="_static/single_dive.html" height="400px" width="100%"></iframe><hr/>




Dive Clusters
*************

The second function ``cluster_summary_plot`` will plot the minimum, maximum, and
mean depth for each cluster. Time is asjusted to be the number of seconds into the dive,
rather than a timestamp.

.. code:: python

  from divebomb.plotting import cluster_summary_plot

  path = '/path/to/results_folder'

  # Plot inside a notebook
  cluster_summary_plot(path, ipython_display=True)

  # Plot out to an HTML file
  cluster_summary_plot(path, ipython_display=False, filename="/Users/alexnunes/Desktop/divebomb/docs/_static/clusters.html")

.. raw:: html

  <iframe src="_static/clusters.html" height="400px" width="100%"></iframe><hr/>




Single DeepDive
***************

.. code:: python

  from divebomb.plotting import plot_from_nc, cluster_summary_plot

  path = '/path/to/results_folder'
  cluster = 0
  dive_id = 59

  # Plot inside a notebook
  plot_from_nc(path, cluster, dive_id, ipython_display=True, type='deepdive)

  # Plot out to an HTML file
  plot_from_nc(path, cluster, dive_id, ipython_display=False, filename='single_deepdive.html', type='deepdive')

.. raw:: html

  <iframe src="_static/single_deepdive.html" height="400px" width="100%"></iframe><hr/>




Clustered DeepDives
*******************

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

  from divebomb import profile_dives
  import pandas as pd
  window = 3600 #seconds

  data = pd.read_csv('/path/to/data.csv')
  corrected_depth_data = correct_depth_offset(data, window=window, aux_file='results/aux_file.nc')

The second wethod uses a rolling average of all surface and near surface values in the time window:

.. code:: python

  from divebomb import profile_dives
  import pandas as pd
  window = 3600 # seconds
  surface_threshold = 4 # meters

  data = pd.read_csv('/path/to/data.csv')
  corrected_depth_data = correct_depth_offset(data, window=window, method='mean', surface_threshold=surface_threshold, aux_file='results/aux_file.nc')
