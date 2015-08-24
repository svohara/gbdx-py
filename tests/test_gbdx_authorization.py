'''
Created on Aug 10, 2015

@author: sohara
'''
import unittest
import os
import sys

package_dir= os.path.dirname( os.path.dirname( os.path.abspath(__file__)) )
sys.path.insert(0, package_dir)

from gbdx.gbdx_auth import get_session

class Test(unittest.TestCase):

    def test_get_session(self):
        print("\nTesting getting gbdx session object.")
        sess = get_session()
        self.assertIsNotNone(sess, "Unable to get a gbdx session object.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_load_credentials']
    unittest.main()