'''
Created on Aug 24, 2015

@author: sohara
'''

import os
import sys
from matplotlib.backends.qt_compat import res
package_dir= os.path.dirname( os.path.dirname( os.path.abspath(__file__)) )
sys.path.insert(0, package_dir)

from gbdx.constants import TEST_AOI, DG_SENSOR_WV2
from gbdx.gbdx_auth import get_session
from gbdx.query import GBDXQuery

def main():
    #get gbdx session object
    gbdx = get_session()
    
    #construct a query object, to search the catalog for
    # images that intersect a given AOI and were created
    # between start and end dates.
    date_range = ('2013-01-15', '2015-01-01')
    qry = GBDXQuery(TEST_AOI, date_range=date_range, platform_name=DG_SENSOR_WV2,
                    max_cloud_cover=5, max_off_nadir_angle=15)
    
    #execute the query. The results will be a GBDXQueryResult object
    res = qry(gbdx)
    print res
    
    #the list of all catalog ids in result set
    cat_ids = res.list_IDs()
    
    #get the pan resolution for the first few cat_ids
    resolutions = [ (cid,res.get_property_from_id(cid,"panResolution")) for cid in cat_ids[0:5]]
    print resolutions

if __name__ == '__main__':
    main()