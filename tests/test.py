
import unittest
import tempfile
import shutil
import numpy as np

from wzone import wzone

class Testfind_ids(unittest.TestCase):
    def test(self):

        # IDs relating to Somalia
        ids = wzone.find_ids(country='Somalia', type_of_violence=1)
        self.assertEqual(ids, [329, 337, 418, 13646])


class Testfind_dates(unittest.TestCase):
    def test(self):

        # dates relating to Somalian Civil War
        dates1 = wzone.find_dates(ids=337, interval='year')[0]
        self.assertEqual(dates1[0], '1989-01-01')
        self.assertEqual(dates1[1], '1990-01-01')
        self.assertEqual(dates1[-1], '2017-01-01')

        dates2 = wzone.find_dates(ids=337)[0]
        self.assertEqual(dates2[0], '1989-02-15')
        self.assertEqual(dates2[1], '2016-12-29')

class Testcheck_params(unittest.TestCase):
    def test(self):

        # parameter values relating to Somalian Civil War
        params = wzone.check_params(337)[0]
        self.assertEqual(params, [0.040224200461589185, 51.985868407453054])

class Testgen_wzones(unittest.TestCase):
    def test(self):

        # Somalia test case
        test_id = 337
        test_dates = ['2000-01-01', '2010-01-01']

        # create war zones
        tmp_dir = tempfile.mkdtemp()
        somalia_path = wzone.gen_wzones(dates=test_dates, ids=test_id, out_dir=tmp_dir, save_novalue_raster=True)

        # check the number of positive predictions
        somalia_mat = np.loadtxt(somalia_path[0], skiprows=6, delimiter=' ', comments='')
        self.assertEqual(somalia_mat.sum(), 0)

        somalia_mat = np.loadtxt(somalia_path[1], skiprows=6, delimiter=' ', comments='')
        self.assertEqual(somalia_mat.sum(), 1986)

        # remove the temporary directory
        shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    unittest.main()
