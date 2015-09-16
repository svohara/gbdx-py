'''
Created on Aug 10, 2015

@author: sohara
'''
import unittest
import os
import sys

PACKAGE_DIR= os.path.dirname( os.path.dirname( os.path.abspath(__file__)) )
sys.path.insert(0, PACKAGE_DIR)

from gbdx import get_session

TEST_CFG_FILE = os.path.join(PACKAGE_DIR,"tests","test_data","test_config_file.txt")

class Test(unittest.TestCase):

    def test_1_get_session(self):
        print("\nTesting getting gbdx session object.")
        sess = get_session()
        self.assertIsNotNone(sess, "Unable to get a gbdx session object.")

    def test_2_expired_token(self):
        print("\nTesting getting gbdx session with saved expired token")
        #TODO: We need to get a 'valid' already-expired token, and save
        # the token data into TEST_CFG_FILE in order for this test to do
        # anything...
        sess = get_session(TEST_CFG_FILE)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_credentials']
    unittest.main()
