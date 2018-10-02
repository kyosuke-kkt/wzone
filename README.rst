Wzone
=====

Wzone is a package for generating zones of armed conflicts. The package contains functionalities 
for querying and creating conflict zones in the `ESRI ASCII raster format`_. The methodological details
can be found `here`_ (TBD). The package greatly relies on the UCDPGED (version 17.1) compiled by
the `Uppsala Conflict Data Program`_.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install git+https://github.com/kyosuke-kkt/wzone.git


An Example
----------------

.. code-block:: python

    import wzone
    import tempfile

    # list of UCDPGED conflict IDs relevant to state-based violence in Somalia
    somalia_ids = wzone.find_ids(country='Somalia', type_of_violence=1)   ### [329, 337, 418, 13646]

    # Yearly sequence of dates from the first to the last events for each conflict
    somalia_dates = wzone.find_dates(ids=somalia_ids, interval='year')   ### somalia_dates[1][0] == '1989-01-01'

    # select a test case
    test_id = 337
    test_date = '2010-01-01'

    # create war zones
    tmp_dir = tempfile.mkdtemp()
    somalia_path = wzone.gen_wzones(dates=test_date, ids=test_id, out_dir=tmp_dir)
    print somalia_path

    # You can continue this example with a variety of functions in other GIS packages.
    ### For arcpy users, refer to arcpy.ASCIIToRaster_conversion function.
    ### For gdal users, refer to gdal.Open function.

Links
-----

* Website: https://github.com/kyosuke-kkt/wzone/
* License: `GPL-3 <https://github.com/kyosuke-kkt/wzone/blob/master/LICENSE>`_

.. _ESRI ASCII raster format: \
    http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/spatial_analyst_tools/esri_ascii_raster_format.htm
.. _here: aa//
.. _Uppsala Conflict Data Program: http://ucdp.uu.se/
.. _pip: https://pip.pypa.io/en/stable/quickstart/