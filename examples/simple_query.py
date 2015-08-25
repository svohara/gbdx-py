'''
Created on Aug 24, 2015

@author: sohara
'''

import os
import sys
import pprint
import time

PACKAGE_DIR = os.path.dirname( os.path.dirname( os.path.abspath(__file__)) )
sys.path.insert(0, PACKAGE_DIR)

import gbdx

def main():
    #get gbdx session object
    session = gbdx.get_session()

    #construct a query object, to search the catalog for
    # images that intersect a given AOI and were created
    # between start and end dates.
    date_range = ('2013-01-15', '2015-01-01')
    qry = gbdx.GBDXQuery(gbdx.TEST_AOI, date_range=date_range,
                         platform_name=gbdx.DG_SENSOR_WV2,
                         max_cloud_cover=5, max_off_nadir_angle=15)

    #execute the query. The results will be a GBDXQueryResult object
    print("-"*40)
    time1 = time.time()
    res = qry(session)
    time2 = time.time()
    print("Query executed in {} seconds".format(time2-time1))

    #note that query results are cached for (default) 300 sec,
    # so if I call this query again immediately, it should use
    # the remembered results.
    time1 = time.time()
    _res2 = qry(session)  #no reason to do this here, other than show caching behavior
    time2 = time.time()
    print("On 2nd attempt, query returned cached results in {} seconds".format(time2-time1))

    print("-"*40)
    print res
    print("-"*40)

    #the list of all catalog ids in result set
    cat_ids = res.list_IDs()

    #get the pan resolution for the first few cat_ids
    resolutions = [ (cid,res.get_property_from_id(cid,"panResolution")) for
                    cid in cat_ids[0:5]]
    for (cid,pan_res) in resolutions:
        print("Image: {}, Pan resolution: {}".format(cid, pan_res))

    print("-"*40)
    print("The 3rd record is:")
    pprint.pprint(res[2])
    print("-"*40)

if __name__ == '__main__':
    main()
