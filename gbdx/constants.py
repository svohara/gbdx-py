'''
Created on Aug 13, 2015
@author: sohara

Package-wide constants
'''
GBDX_BASE_URL = "https://geobigdata.io"
GBDX_AUTH_URL = "https://geobigdata.io/auth/v1/oauth/token"

GBDX_WORKFLOW_STATES = ("submitted", "scheduled", "started",
                        "canceled", "cancelling", "failed",
                        "succeeded", "timedout", "pending",
                        "running", "complete", "all")


DG_SENSOR_WV3 = "WORLDVIEW03"
DG_SENSOR_WV2 = "WORLDVIEW02"
DG_SENSOR_WV1 = "WORLDVIEW01"
#DG_SENSOR_GEO = "GEOEYE01" ??

TEST_ORDER_NUM = "054581653"
TEST_CAT_ID = "1030010006C85000"
TEST_AOI = (-122.44535716344512, 47.114994482489955,
            -122.38750565914782, 47.21057522872027)


if __name__ == '__main__':
    pass