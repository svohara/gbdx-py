'''
Created on Aug 10, 2015

@author: sohara
'''
import unittest
import os
import sys
import shapely.geometry as sg

PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PACKAGE_DIR)

from gbdx import get_session, GBDXQuery, TEST_AOI

class Test(unittest.TestCase):
    def setUp(self):
        self.session = get_session()
        
    def test_A_perform_query(self):
        print("\nTesting simple catalog query")
        query = GBDXQuery(TEST_AOI)
        result = query(self.session)
        self.assertTrue( len(result) > 10, "Unexpectedly few results for test query")

        cat_id_list = result.list_IDs()
        poly = result.get_footprint_from_id(cat_id_list[0])
        self.assertIsInstance(poly, sg.Polygon, "Expected a shapely polygon output.")
        pan_res = float(result.get_property_from_id(cat_id_list[0], 'panResolution'))
        self.assertIsNotNone(pan_res, "Unexpected None return from a property query.")

        with self.assertRaises(KeyError):
            _record = result.get_record_for_ID('not_gonna_find_me')

    def test_B_date_query(self):
        print("\nTesting date-filtered catalog query")
        dates = ('2010-01-01','2015-01-01')
        query = GBDXQuery(TEST_AOI, date_range=dates)
        result = query(self.session)
        self.assertTrue( len(result) == 46, "There should be 46 records returned.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_credentials']
    unittest.main()
