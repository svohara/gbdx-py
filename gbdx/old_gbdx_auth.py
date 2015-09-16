"""
Module for establishing an OAuth2 session
with the GBDX platform.

Written by Nate Ricklin, Patrick Young, Stephen O'Hara
"""

import os
import base64
import json
from ConfigParser import ConfigParser, NoOptionError

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from functools import partial

from .constants import GBDX_AUTH_URL

def get_session(config_file=None):
    """Returns a requests session object with oauth enabled for
    interacting with GBDX end points."""

    def save_token(token_to_save):
        """Save off the token back to the config file."""
        if not 'gbdx_token' in set(cfg.sections()):
            cfg.add_section('gbdx_token')
        cfg.set('gbdx_token', 'json', json.dumps(token_to_save))
        with open(config_file, 'w') as sink:
            cfg.write(sink)

    # Read the config file (ini format).
    cfg = ConfigParser()
    if not config_file:
        config_file = os.path.expanduser('~/.gbdx-config')
    if not cfg.read(config_file):
        raise RuntimeError('No ini file found at {} to parse.'.format(config_file))

    try:
        client_id = cfg.get('gbdx', 'client_id')
        client_secret = cfg.get('gbdx', 'client_secret')
        api_key = base64.b64encode("{}:{}".format(client_id, client_secret))
    except NoOptionError:
        #user probably was given an apikey instead
        api_key = cfg.get('gbdx','api_key')
        (client_id, client_secret) = _unpack_apikey(api_key)

    # See if we have a token stored in the config, and if not, get one.
    if 'gbdx_token' in set(cfg.sections()):
        # Parse the token from the config.
        token = json.loads(cfg.get('gbdx_token','json'))

        # Note that to use a token from the config, we have to set it
        # on the client and the session!
        
        #TODO: Steve says this doesn't work correctly when a token is completely
        # expired...trying to use the token raises KeyError because 'access_token'
        # key doesn't exist...
        sess = OAuth2Session(client_id, client=LegacyApplicationClient(client_id, token=token),
                          auto_refresh_url=cfg.get('gbdx','auth_url'),
                          auto_refresh_kwargs={'client_id':client_id,
                                               'client_secret':client_secret},
                          token_updater=save_token)
        sess.token = token
    else:
        # No pre-existing token, so we request one from the API.
        sess = OAuth2Session(client_id, client=LegacyApplicationClient(client_id),
                          auto_refresh_url=cfg.get('gbdx','auth_url'),
                          auto_refresh_kwargs={'client_id':client_id,
                                               'client_secret':client_secret},
                          token_updater=save_token)

        # Get the token and save it to the config.
        headers = {"Authorization": "Basic {}".format(api_key),
                   "Content-Type": "application/x-www-form-urlencoded"}
        token = sess.fetch_token(cfg.get('gbdx','auth_url'),
                              username=cfg.get('gbdx','user_name'),
                              password=cfg.get('gbdx','user_password'),
                              headers=headers)
        save_token(token)

    #sess.post = partial(_post, sess) #see note below on _post method...
    return sess

def _unpack_apikey(apikey):
    """
    Converts an api key into client_id and client_secret values
    """
    tmp = apikey.split(':')
    client_id = tmp[0]
    client_secret = ":".join(tmp[1:])
    return (client_id, client_secret)

# TODO The following function is basically monkey-patching,
#    so there might be a much cleaner way to do this with
#    setting a default header in the OAuth2 session object??
def _post(sess, url, data=None, **kwargs):
    """
    Replacement for the OAuth2Session object to provide
    an easier to use post method, where the default headers
    use json payloads.
    """
    token = sess.token['access_token']
    default_headers = {'Authorization':'Bearer {}'.format(token),
                       'Content-Type':'application/json'}
    if not 'headers' in kwargs:
        kwargs['headers'] = default_headers
    ret = sess.request("POST", url, data=data, **kwargs)
    return ret

def configure(config_file=None):
    """
    Prompts user for the basic credentials required to generate
    the ~/.gbdx-config file.
    """
    #collect the configuration data from the user...
    config_data = {"auth_url":GBDX_AUTH_URL}
    print("Please provide the following information.")
    config_data['user_name'] = raw_input("user_name: ")
    config_data['user_password'] = raw_input("user_password: ")

    #TODO: I haven't had much luck being able to copy-paste in
    # an apikey and not have encoding problems, like what happens
    # with "\" as a character creating an escape, etc...
    #apikey = raw_input("api_key: ")
    #if not apikey:
    #    config_data['client_id'] = raw_input("client_id: ")
    #    config_data['client_secret'] = raw_input("client_secret: ")
    #else:
    #    config_data['api_key'] = apikey
    config_data['client_id'] = raw_input("client_id: ")
    config_data['client_secret'] = raw_input("client_secret: ")
    #save data to a new config file
    cfg = ConfigParser()
    cfg.add_section("gbdx")
    for (key,value) in config_data.iteritems():
        cfg.set("gbdx", key, value)
    if not config_file:
        config_file = os.path.expanduser('~/.gbdx-config')
    with open(config_file, 'w') as cfg_file:
        cfg.write(cfg_file)

