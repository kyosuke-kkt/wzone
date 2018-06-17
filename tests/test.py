
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
