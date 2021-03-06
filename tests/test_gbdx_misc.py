'''
Created on Aug 10, 2015

@author: sohara
'''
import unittest
import os
import sys 

PACKAGE_DIR= os.path.dirname( os.path.dirname( os.path.abspath(__file__)) )
sys.path.insert(0, PACKAGE_DIR)

import gbdx

class Test(unittest.TestCase):
    def setUp(self):
        self.session = gbdx.get_session()

    def test_get_order_status(self):
        print("\nTesting get_order_status")
        order_status = gbdx.get_order_status(self.session, gbdx.TEST_ORDER_NUM)
        self.assertTrue('salesOrderNumber' in order_status, "Error with order status.")
        #there should be only a single line-item in this order
        line_item = order_status['lines'][0]
        self.assertEqual(line_item['percentDelivered'],'100',
                         "Error with line item. Expected 100 percent delivered.")

    def test_get_thumbnail(self):
        print("\nTesting get_thumbnail")
        img = gbdx.get_thumbnail(self.session, gbdx.TEST_CAT_ID, show=False)
        #img is an ndarray / openCV image
        self.assertTupleEqual(img.shape, (409,512,3),
                "Error with get_thumbnail. Unexpected img shape.")

    def test_get_catalog_record(self):
        print("\nTesting get catalog record")
        rec = gbdx.get_catalog_record(self.session, gbdx.TEST_CAT_ID)
        self.assertTrue( rec['identifier']==gbdx.TEST_CAT_ID,
                         "Unexpected identifier returned in catalog record")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_credentials']
    unittest.main()