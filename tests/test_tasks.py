'''
Created on Sep 16, 2015

@author: sohara
'''
import unittest
import sys
import os
PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PACKAGE_DIR)

import gbdx

class Test(unittest.TestCase):
    def setUp(self):
        self.sess = gbdx.get_session()

    def test_list_tasks(self):
        print("\nTesting list available tasks")
        task_list = gbdx.list_available_tasks(self.sess)
        self.assertTrue(len(task_list)>5, "Suspiciously few tasks listed on gbdx platform.")
    
    def test_task_definition(self):
        print("\nTesting get task definition")
        task_list = gbdx.list_available_tasks(self.sess)
        ret = gbdx.get_task_definition(self.sess, task_list[0])
        self.assertTrue("description" in ret.keys(), "Possibly invalid return for task definition")

    def test_search_workflows(self):
        print("\nTesting searching workflows")
        (workflow_ids, _) = gbdx.search_workflows(self.sess, state="all", owner=None,
                                                  lookback_h=24, details=False, verbose=False)
        self.assertTrue(len(workflow_ids)>1, "Suspiciously few workflows in the past 24 hours returned.")
        
        print("\nTesting getting workflow details")
        w_id = workflow_ids[0]
        w_status = gbdx.get_workflow_status(self.sess, w_id)
        self.assertTrue("owner" in w_status.keys(), "Possibly invalid return for workflow status")
        
        print("\nTesting summarizing workflow tasks")
        summary = gbdx.summarize_workflow_tasks(w_status)
        print summary
        self.assertTrue(len(summary)>0, "Task summary is empty")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()