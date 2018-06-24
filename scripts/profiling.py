
import wzone
import tempfile
import shutil
import cProfile

# select a test case
test_id = 337
test_date = ['2000-01-01', '2000-01-02', '2010-01-01', '2010-01-02', '2010-01-03']

# create war zones for the first conflict ID (only the first year for the purpose of test)
tmp_dir = tempfile.mkdtemp()
cProfile.run('wzone.gen_wzones(dates=test_date, ids=test_id, out_dir=tmp_dir)', sort='tottime')

# remove the temporary directory
shutil.rmtree(tmp_dir)

