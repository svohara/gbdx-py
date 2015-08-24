"""
Created on Aug 5, 2015
@author: Stephen O'Hara

This module exposes convenience functions that
are wrappers to various GBDX RESTful API calls.
"""
import os
import numpy as np
from io import BytesIO

#Fancy importing to allow the user to use
# either openCV or matplotlib for image rendering
_IMAGE_ENGINE = None
try:
    import pylab as pl
    _IMAGE_ENGINE = "pylab"
except ImportError:
    try:
        import cv2
        _IMAGE_ENGINE = "opencv"
    except ImportError:
        print("Either pylab (matplotlib) or openCV must be installed \
            to view thumbnails")

from .constants import GBDX_BASE_URL

def get_json(session, url):
    """
    Wrapper for session.get() when you want to get
    the results as json. Handles the boiler plate
    code for checking the result status and converting
    result to json
    """
    ret = session.get(url)
    ret.raise_for_status()
    return ret.json()

def post_json(session, url, payload):
    """
    Wrapper for session.post() when you want to get
    the results as json. Handles the boilder plate
    code for checking the result status and converting
    the result to json.
    """
    ret = session.post(url, data=payload)
    ret.raise_for_status()
    return ret.json()

def get_s3creds(session, duration=3600):
    url = os.path.join(GBDX_BASE_URL, "s3creds","v1","prefix?duration={}".format(duration))
    s3_data = get_json(session, url)    
    s3_url = "s3://{bucket}/{prefix}".format(**s3_data)
    return (s3_url, s3_data)

def get_order_status(session, soli):
    """
    Retrieves the status information for a specified imagery order.
    @param session: The gbdx session, from gbdx_auth.get_session.
    @param soli: The order number, or 'soli'
    @return: A dictionary that provides the order status information.
    """
    url = os.path.join(GBDX_BASE_URL,'orders','v1','status',soli)
    return get_json(session, url)

def get_catalog_record(session, cat_id):
    """
    Retrieves the catalog record for the image with given cat_id,
    if one exists.
    @param session: The gbdx session, from gbdx_auth.get_session.
    @param cat_id: The image catalog id
    @return: A dictionary with the record information or None
    """
    url = os.path.join(GBDX_BASE_URL, "catalog","v1", "record", cat_id)
    return get_json(session, url)

def get_thumbnail(session, cat_id, show=True):
    """
    Gets an openCV image of the catalog thumbnail for a given catalog id. Optionally
    displays that thumbnail in a window.
    @param session: The gbdx session, from gbdx_auth.get_session.
    @param cat_id: The catalog id for the image of interest
    @param show: If true, after the thumbnail image is retrieved, it will be displayed
    in a freestanding window.
    @return: An open-cv image, represented as a numpy ndarray. Can be manipulated using
    openCV functions, saved to disk, or whatever the user desires.
    """
    url = os.path.join(GBDX_BASE_URL,'thumbnails','v1','browse','{}.medium.png'.format(cat_id))
    ret = session.get(url)
    ret.raise_for_status()
    buf = ret.content
    img = _decode_img(buf)
    if show:
        _show_img(img, window_title=str(cat_id))
    return img

def _decode_img_openCV(buf):
    #pylint: disable=E1103
    img_data = np.fromstring(buf, np.uint8)
    img = cv2.imdecode(img_data, flags=cv2.CV_LOAD_IMAGE_UNCHANGED)
    #pylint: enable=E1103
    return img

def _show_img_openCV(cvimg, window_title='Image Thumbnail'):
    #pylint: disable=E1103
    cv2.imshow(window_title, cvimg)
    cv2.waitKey(0)
    cv2.destroyWindow(window_title)
    #pylint: enable=E1103

def _decode_img_pylab(buf):
    img = pl.imread(BytesIO(buf))
    return img

def _show_img_pylab(img, window_title='Image Thumbnail'):
    pl.figure()
    pl.imshow(img)
    pl.title(window_title)
    pl.show()

# Function aliases to map generic function
# to that provided by a specific image engine
if _IMAGE_ENGINE == "pylab":
    _decode_img = _decode_img_pylab
    _show_img = _show_img_pylab
else:
    _decode_img = _decode_img_openCV
    _show_img = _show_img_openCV

if __name__ == '__main__':
    pass
