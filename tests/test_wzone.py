
# A light module for testing

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

        # nu and gamma values for Somalia (time-variant)
        params = wzone.check_params(337, with_date=True)
        self.assertEqual(params, [[0.047148038245961095, 28.401796201000675]])

        # nu and gamma values for Somalia (time-invariant)
        params = wzone.check_params(337, with_date=False)
        self.assertEqual(params, [[0.05703923508077811, 93.8623468254216]])

class Testgen_wzones(unittest.TestCase):
    def test(self):

        # Somalia test case
        test_id = 337
        test_dates = ['2000-01-01', '2010-01-01']

        # create war zones
        tmp_dir = tempfile.mkdtemp()
        somalia_path1 = wzone.gen_wzones(dates=test_dates, ids=test_id, out_dir=tmp_dir)
        somalia_path2 = wzone.gen_wzones(dates=None, ids=test_id, out_dir=tmp_dir)

        # check the number of positive predictions
        somalia_mat1 = np.loadtxt(somalia_path1[0], skiprows=6, delimiter=' ', comments='')
        self.assertEqual(somalia_mat1.sum(), 257)

        somalia_mat2 = np.loadtxt(somalia_path1[1], skiprows=6, delimiter=' ', comments='')
        self.assertEqual(somalia_mat2.sum(), 2333)

        somalia_mat3 = np.loadtxt(somalia_path2[0], skiprows=6, delimiter=' ', comments='')
        self.assertEqual(somalia_mat3.sum(), 2528)

        # remove the temporary directory
        shutil.rmtree(tmp_dir)

if __name__ == '__main__':
    unittest.main()
