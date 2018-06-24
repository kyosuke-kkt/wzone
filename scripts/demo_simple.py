
import wzone
import numpy as np

# list of UCDPGED conflict IDs relevant to state-based violence in Somalia
somalia_ids = wzone.find_ids(country='Somalia', type_of_violence=1)   ### [329, 337, 418, 13646]

# Yearly sequence of dates from the first to the last events for each conflict
somalia_dates = wzone.find_dates(ids=somalia_ids, interval='year')   ### somalia_dates[1][0] == '1989-01-01'

# select a test case
test_id = 337
test_date = ['2000-01-01', '2010-01-01']

# create war zones for the first conflict ID (only the first year for the purpose of test)
out_paths = wzone.gen_wzones(dates=test_date, ids=337, out_dir='C:/Users/Kyosuke/Desktop')

# read and count the number of cells within conflict zones
out_mat = np.loadtxt(out_paths[0], skiprows=6, delimiter=' ', comments='')
print out_mat.shape
print out_mat.sum()

