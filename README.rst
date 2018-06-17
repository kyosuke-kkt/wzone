Wzone
=====

Wzone is a package for generating zones of armed conflicts. The package contains functionalities 
for querying and creating conflict zones in the `ESRI ASCII raster format`_. The methodological details
can be found `here`_. The package greatly relies on the UCDPGED (version 17.1) compiled by
the `Uppsala Conflict Data Program`_.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

    pip install --index-url https://test.pypi.org/simple/ wzone


An Example
----------------

.. code-block:: python

    from wzone import wzone

    # list of UCDPGED conflict IDs relevant to state-based violence in Somalia
    somalia_ids = wzone.find_ids(country='Somalia', type_of_violence=1)

    # Yearly sequence of dates from the first to the last events for each conflict
    somalia_dates = wzone.find_dates(ids=somalia_ids, interval='year')

    # select the test case
    test_ids = somalia_ids[1]       ### 337
    test_dates = somalia_dates[1]   ### corresponding dates

    # create war zones for the first conflict ID (only the first 5 years for the purpose of test)
    somalia_paths = wzone.gen_wzones(dates=test_dates[0:4], ids=test_ids, out_dir='')

    # print the locations in which the war zone data are saved
    print somalia_paths

Links
-----

* Website: https://github.com/kyosuke-kkt/wzone/
* License: `MIT <https://github.com/kyosuke_kkt/wzone/LICENSE>`_
* Releases: https://pypi.org/project/wzone/

.. _ESRI ASCII raster format: \
    http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/spatial_analyst_tools/esri_ascii_raster_format.htm
.. _here: aa//
.. _Uppsala Conflict Data Program: http://ucdp.uu.se/
.. _pip: https://pip.pypa.io/en/stable/quickstart/