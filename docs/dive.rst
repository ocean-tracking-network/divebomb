.. _dive_page:


Dive Class
----------

The Dive class is used to encapsulate all the attriutes of a dive and the data needed
to reconstruct a plot of the dive.

.. currentmodule:: divebomb.Dive

.. autoclass:: Dive.Dive
   :members: __init__,
    get_descent_duration,
    get_ascent_duration,
    get_surface_duration,
    get_descent_velocity,
    get_ascent_velocity,
    set_bottom_variance,
    set_dive_variance,
    set_skew,
    get_peaks,
    to_dict,
    plot
