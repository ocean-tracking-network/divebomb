.. _dive_page:


Dive Class
----------

The Dive class is used to encapsulate all the attributes of a dive and the data
needed to reconstruct a plot of the dive. The ``at_depth_threshold`` defaults
to ``0.15`` which means anything below ``85%`` of the depth of the
dive is considered to be at depth.

``surface_threshold`` is used to determine how shallow the animal should be
before it is considered to be at the surface. It defualts tp ``0`` but can be
adjusted if the animal is large or you want a larger depth window for surface
behaviours. ``surface_threshold`` should be passed in meters.

.. currentmodule:: divebomb.Dive

.. autoclass:: Dive.Dive
  :members:
  :undoc-members:
  :private-members:
