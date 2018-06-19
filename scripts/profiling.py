
from wzone import wzone
import tempfile
import shutil
import numpy as np
import cProfile

# list of UCDPGED conflict IDs relevant to state-based violence in Somalia
somalia_ids = wzone.find_ids(country='Somalia', type_of_violence=1)   ### [329, 337, 418, 13646]

# Yearly sequence of dates from the first to the last events for each conflict
somalia_dates = wzone.find_dates(ids=somalia_ids, interval='year')   ### somalia_dates[1][0] == '1989-01-01'

# select a test case
test_id = 337
test_date = ['2000-01-01', '2000-01-02', '2010-01-01', '2010-01-02', '2010-01-03']

# create war zones for the first conflict ID (only the first year for the purpose of test)
tmp_dir = tempfile.mkdtemp()
somalia_path = wzone.gen_wzones(dates=test_date, ids=test_id, out_dir='C:/Users/Kyosuke/Desktop')

# profiling
cProfile.run('wzone.gen_wzones(dates=test_date, ids=test_id, out_dir=tmp_dir)', sort='tottime')

# read and count the number of cells within conflict zones
somalia_mat = np.loadtxt(somalia_path[0], skiprows=6, delimiter=' ', comments='')
print somalia_mat.shape   ### (1800, 3600)
print somalia_mat.sum()   ### 1986

# remove the temporary directory
del somalia_mat
shutil.rmtree(tmp_dir)

