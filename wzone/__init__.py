
import os
import zipfile
import pkg_resources

pkl_file = pkg_resources.resource_filename('wzone', 'data/ged_estimated_osvm.pkl')
zip_file = pkg_resources.resource_filename('wzone', 'data/ged_estimated_osvm.pkl')[0:-4] + '.zip'
if not os.path.exists(pkl_file):
    with zipfile.ZipFile(zip_file, 'r') as zf:
        zf.extractall('data/')
