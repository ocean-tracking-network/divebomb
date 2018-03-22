.. divebomb documentation master file, created by
   sphinx-quickstart on Fri Dec 15 13:30:39 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.md


.. _installation:

Installation
------------

Divebomb can be installed using Pip or through a Conda environment.

Conda
*****

.. code:: bash

  conda config --add channels ioos
  conda config --add channels cbetters
  conda config --add channels anaconda
  conda install -c anunes divebomb



Pip
***

.. code:: bash

  pip install --extra-index-url https://testpypi.python.org/pypi divebomb


.. _implementation:

Use
---

Pass a Pandas DataFrame to the function with a ``time`` and a ``depth`` (in positive meters) column. Provide the length of animal using ``animal_length`` (in meters).
Refine other arguments as needed.

.. code:: python

  profile_dives(data, animal_length, folder=None, columns={'depth': 'depth', 'time': 'time'}, acceleration_threshold=0.015, n_clusters=5, ipython_display_mode=False)


The dive data can either be displayed to the user in Jupyter Notebooks or stored in files. Displaying will not
cluster the dives, but show them in ascending order by time in an iPython Notebook.

.. code:: python

  # Display
  animal_length = 3 # in meters
  profile_dives(df, ipython_display_mode=True, animal_length=animal_length)

  # Store in files
  profile_dives(df, folder='result', animal_length=animal_length)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   divebomb_functions
   dive
   plotting
