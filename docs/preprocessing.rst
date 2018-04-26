.. _preprocessing_functions_page:


Preprocessing Functions
-----------------------

The preprocessing module is used help correct dive drift and offsets. The offset is
calculated using a rolling time window, similar to what is explained `here <http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0015850>`_.

There are two methods for the main function, ``correct_depth_offset()``:

* max: zeros the local maxium and uses the difference as the offset for the rest
* mean: uses the time window and a maximum depth to look for the average offset within the window




.. currentmodule:: divebomb.preprocessing

.. automodule:: divebomb.preprocessing
    :members:
