import wzone

# list of UCDPGED conflict IDs relevant to state-based violence in Somalia
somalia_ids = wzone.find_ids(country='Somalia', type_of_violence=1)

# Yearly sequence of dates from the first to the last events for each conflict
somalia_dates = wzone.find_dates(ids=somalia_ids, interval='year')

# create war zones for the first conflict ID (only the first 5 years for the purpose of test)
somalia_paths = wzone.gen_wzones(dates=somalia_dates[0][0:4], ids=somalia_ids[0], out_dir='')

# print the output file locations
print somalia_paths
