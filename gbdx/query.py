'''
Created on Aug 7, 2015

@author: Stephen O'Hara

This module defines a gbdx catalog query object
and related functions for performing imagery
queries.
'''
import time
import json

try:
    import shapely.geometry as sg
    import shapely.wkt as swkt
except ImportError:
    print "You must have the shapely library installed for spatial queries."

from gbdx import GBDX_BASE_URL, DG_SENSOR_WV2, TEST_AOI, get_session, post_json

class GBDXQuery(object):
    """
    This class is used to define a query object, which encapsulates
    the catalog query parameters desired by the user.
    """
    QUERY_CACHE_DURATION = 300 #seconds

    def __init__(self, AOI, date_range=(None,None),
                 platform_name=DG_SENSOR_WV2,
                 max_cloud_cover=5,
                 max_off_nadir_angle=15):
        """
        Constructor
        @param AOI: A shapely polygon object in WGS84 LON/LAT coordinates, from which
        a bounding box will be computed, or an input list/tuple as (lon0, lat0, lon1, lat1)
        @param date_range: A tuple (start_date, end_date), where the dates are specified
        as zero-padded YYYY-MM-DD strings. You may specify None as well. For example,
        to filter based on a start date you can set date_range=(2010-01-01, None).
        @param platform_name: DG_SENSOR_WV2, for example
        """
        self.AOI = AOI
        if date_range:
            self.start_date, self.end_date = date_range
        else:
            self.start_date = self.end_date = None
        self.platform_name = platform_name
        self.max_cloud = max_cloud_cover
        self.max_off_nadir = max_off_nadir_angle
        self._last_query_results = None
        self._last_query_time = None
        self.refresh()

    def _get_bounds(self, AOI):
        if isinstance(AOI, sg.Polygon):
            return AOI.bounds
        else:
            return sg.box(*AOI)

    def _construct_filter_list(self):
        filters_list = [
            "sensorPlatformName = '{}'".format(self.platform_name),
            "cloudCover < {}".format(self.max_cloud),
            "offNadirAngle between 1 and {} ".format(self.max_off_nadir)
        ]
        return filters_list

    def _construct_search_criteria(self):
        search_criteria = {}
        search_criteria['searchAreaWkt'] = self._get_bounds(self.AOI).wkt
        search_criteria['startDate'] = self.start_date
        search_criteria['endDate'] = self.end_date
        search_criteria['filters'] = self._construct_filter_list()
        search_criteria['tagResults'] = False
        search_criteria['types']=["DigitalGlobeAcquisition"]
        return search_criteria

    def refresh(self):
        """
        Re-constructs the search criteria data structure from any new
        data values set, and clears out any _last_query_results
        """
        self._last_query_results = None
        self._last_query_time = None
        self.search_body = self._construct_search_criteria()

    def __str__(self):
        return str(self.search_body)

    def __call__(self, session):
        """
        Execute the query using the given session
        """
        return self.query(session)

    def query(self, session):
        """
        Queries the gbdx catalog and returns the results.
        Note that this object caches the query results,
        so that multiple calls to this method with no
        other changes will result in only one call to the
        network (unless the cache expiration period has elapsed).
        If you have changed the query parameters, such as
        by setting a new AOI value, you MUST call the
        refresh() method before performing a new query,
        or you will get the results from the old parameters.
        @param session: The gbdx session object
        """
        query_start = time.time()
        if self._last_query_results:
            if query_start < self._last_query_time + \
                             GBDXQuery.QUERY_CACHE_DURATION:
                #use cached results
                return GBDXQueryResult(self._last_query_results)

        payload = json.dumps(self.search_body)
        url = "/".join([GBDX_BASE_URL,'catalog','v1','search'])

        json_res = post_json(session, url, payload)
        #res = session.post(url, data=payload)
        #res.raise_for_status()
        #json_res = res.json()

        self._last_query_results = json_res
        self._last_query_time = query_start

        query_results = GBDXQueryResult(json_res)

        return query_results

class GBDXQueryResult(object):
    """
    A utility class to provide easy-to-use methods
    for quickly extracting commonly-used information
    from a catalog query result structure
    """
    def __init__(self, results_dict):
        self.stats = results_dict['stats']
        self.search_tag = results_dict['searchTag']
        self.results = self._get_sorted_results(results_dict['results'])

    def _get_sorted_results(self, raw_results):
        tmp = sorted( [ (record['identifier'], record) for record in raw_results])
        return [rec for (_,rec) in tmp]

    def __len__(self):
        return self.stats['totalRecords']

    def __getitem__(self, i):
        if self.results is None:
            raise KeyError("Result set is empty!")
        try:
            record = self.results[i]
        except TypeError:
            #not an index input, so let's try
            # retrieval by identifier...
            record = self.get_record_for_ID(i)
        return record

    def __str__(self):
        str1 = "Query Result: {recordsReturned} records returned\n".format(**self.stats)
        id_list = self.list_IDs()
        if len(id_list) > 5:
            str2 = "\n".join(id_list[0:5]+["..."])
        else:
            str2 = "\n".join(id_list)
        return str1+str2

    def __repr__(self):
        return str(self)

    def get_record_for_ID(self, ID):
        """
        Finds the record within the result set
        for the given id (cat_id), if one exists.
        Raises KeyError otherwise.
        """
        for record in self:
            if record['identifier'] == ID:
                break
        else:
            raise KeyError("Result set does not contain {}".format(ID))
        return record

    def list_IDs(self):
        """
        Lists the identifiers (cat_ids) for all the results
        """
        return sorted( [r['identifier'] for r in self] )

    def list_property_keys(self):
        """
        This method returns the available property keys
        in the result items. It makes the assumption that
        all keys are the same for all results, and is
        thus a convenience function for the user, especially
        when using this code interactively.
        """
        _tmp = self[0]
        return _tmp['properties'].keys()

    def get_property_from_id(self,ID,key):
        """
        gets the value of a given property for
        a given ID (cat_id)
        @param ID: A cat_id in this list of results
        @param key: The property name to return, such
        as 'panResolution'. See self.list_property_keys()
        to get a list of valid property keys.
        """
        rec = self.get_record_for_ID(ID)
        return rec['properties'][key]

    def get_footprint_from_id(self, ID):
        """
        Returns a shapely polygon of the footprint
        of the image referenced by ID
        """
        f = self.get_property_from_id(ID, 'footprintWkt')
        return swkt.loads(f)

def get_test_query_results():
    """
    Convenience function to quickly get a testing result set.
    This is useful when demonstrating via an interactive IPython shell, etc.
    """
    gbdx = get_session()
    qry = GBDXQuery(TEST_AOI)
    res = qry(gbdx)
    return res

if __name__ == '__main__':
    pass
