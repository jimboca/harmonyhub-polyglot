#
# TODO:
#
#

import os,sys
from polyglot.nodeserver_api import Node
from functools import partial
from harmony_hub_nodes import *
from harmony_hub_funcs import myint,myfloat,ip2long,long2ip
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR

sys.path.insert(0,"../pyharmony")
#import pyharmony
from pyharmony import ha_get_token,ha_get_client

class HarmonyHub(Node):
    """ 
    The Main Node for a single Harmony Hub
    """

    def __init__(self, parent, primary, manifest=None, config_data=None, address=None):
        self.parent      = parent
        self.connected   = 0
        self.parent.logger.info("HarmonyHub:init: Adding manifest=%s upd_data=%s" % (manifest,config_data))
        self.status = {}
        self.current_activity = -1
        # Use manifest values if passed in.
        if manifest is not None:
            self.name  = manifest['name']
            if address is None:
                # TODO: Look up node address in config data.
                self.parent.send_error("HarmonyHub:init:%s: address must be passed in when using manifest for: " % (name,manifest))
                return False
            self.address = address
            # TODO: It's ok to not have drivers?  Just let query fill out the info? 
            if not 'drivers' in manifest:
                self.parent.send_error("HarmonyHub:init:%s: no drivers in manifest: " % (name,manifest))
                return False
            drivers = manifest['drivers']
            # Get the things we need from the drivers, the rest will be queried.
            self.host  = long2ip(drivers['GV1'])
            self.port  = drivers['GV2']
            # TODO: Is the node_def_id in the manifest?
        elif config_data is not None:
            self.node_def_id = address
            self.name      = config_data['name']
            if address is None:
                self.parent.send_error("HarmonyHub:init:%s: address not passed in")
                return False
            self.address   = address.lower()
            self.host      = config_data['host']
            self.port      = 5222
        else:
            self.parent.send_error("HarmonyHub:init:%s: One of manifest or udp_data must be passed in." % (address))
            return False
        # Add the Hub
        self.parent.logger.info("HarmonyHub:init: Adding %s %s %s" % (self.address, self.name, self.address))
        super(HarmonyHub, self).__init__(parent, self.address, self.name, primary, manifest)
        self.set_driver('ST',   0, uom=2, report=True)
        # TODO: Trap ip2long failure when bad address is specified.
        self.set_driver('GV1',  ip2long(self.host), uom=56, report=True)
        self.set_driver('GV2',  self.port, uom=56, report=True)
        self.token  = None
        self.client = None
        # Call query to pull the info from the hub.
        self.query();
        # Force report on startup
        self.report_driver()
        self.parent.logger.info("HarmonyHub:init: Done adding hub '%s' '%s' %s" % (self.address, self.name, self.address))

    def query(self, **kwargs):
        """ query the hub """
        if self.client is None:
            self.parent.logger.info("HarmonyHub:query: Initializing PyHarmony Client")
            # TODO: Fail if get_token fails
            self.token  = ha_get_token(self.host, self.port)
            self.client = ha_get_client(self.token, self.host, self.port)
            self.parent.logger.info("HarmonyHub:query: PyHarmony Client: " + str(self.client))
        self.parent.logger.debug("HarmonyHub:query:start:%s" % (self.name))
        self.set_driver('ST', 1, uom=2, report=True)
        # TODO: Poll the hub to get the activity and set it.
        ca = self.client.get_current_activity()
        if int(ca) != self.current_activity:
            self._set_current_activity(ca)
        self.parent.logger.debug("HarmonyHub:query:done:%s" % (self.name))
        return True

    def poll(self):
        self.parent.logger.debug("HarmonyHub:poll:%s:" % (self.name))
        self.query()
        return

    def long_poll(self):
        self.parent.logger.debug("HarmonyHub:long_poll:%s:" % (self.name))
        # get_status handles properly setting self.connected and the driver
        # so just call it.
        #self._get_status()
    
    def add_device(self,config_data):
        return HarmonyDevice(self.parent, self, manifest=None, config_data=config_data)

    def _set_current_activity(self, value):
        """ 
        Update Polyglot with the current activity.
        """
        val = myint(value)
        if val == -1:
            val = 0
        self.current_activity = val
        self.parent.logger.debug("HarmonyHub:_set_current_activity:%s: %d" % (self.name,self.current_activity))
        self.set_driver('GV3', 0, uom=25, report=True)
        self.set_driver('GV3', self.current_activity, uom=25, report=True)
        self.parent.logger.debug("HarmonyHub:_set_current_activity:%s: get=%s" % (self.name,self.get_driver('GV3')[0]))
        return True

    def _cmd_set_current_activity(self, **kwargs):
        """ 
        This runs when ISY changes the current current activity
        """
        val = myint(kwargs.get("value"))
        self.parent.logger.debug("HarmonyHub:_cmd_set_current_activity:%s: %d" % (self.name,val))
        sv = self.current_activity
        self._set_current_activity(val)
        # Push it to the Hub
        if self.client is None:
            self.parent.logger.error("HarmonyHub:_cmd_set_activity:%s: No Client" % (self.name))
            ret = False
        else:
            if val == 0:
                val = -1
            ret = self.client.start_activity(val)
            self.parent.logger.debug("HarmonyHub:_cmd_set_activity:%s: %d result=%s" % (self.name,val,str(ret)))
        if not ret:
            # Was not able to update the hub, tell polyglot.
            self._set_current_activity(sv)
        return ret
        
    _drivers = {
        'ST':  [0, 2,  myint],
        'GV1': [0, 56, myint],
        'GV2': [0, 56, myint],
        'GV3': [0, 25, myint],
    }
    """ Driver Details:
    ST:   boolean: Responding
    GV1:  unsigned integer: IP Address
    GV2:  integer: Port
    GV3:  integer: Activity
    """
    _commands = {
        'QUERY': query,
        'SET_ACTIVITY': _cmd_set_current_activity,
    }

    # The nodeDef id of this camers.
    node_def_id = 'HubDefault'

    
