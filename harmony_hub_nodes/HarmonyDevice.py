#
# TODO:
#
#

import os,sys
from polyglot.nodeserver_api import Node
from functools import partial
from harmony_hub_funcs import myint,myfloat,ip2long,long2ip
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR

class HarmonyDevice(Node):
    """ 
    The Main Node for a single Harmony Hub
    """

    def __init__(self, parent, primary, manifest=None, config_data=None, address=None):
        self.parent      = parent
        self.parent.logger.info("HarmonyDevice:init: Adding manifest=%s config_data=%s" % (manifest,config_data))
        self.status = {}
        # Use manifest values if passed in.
        if manifest is not None:
            self.name  = manifest['name']
            if address is None:
                # TODO: Look up node address in config data.
                self.parent.send_error("HarmonyDevice:init:%s: address must be passed in when using manifest for: " % (name,manifest))
                return False
            self.address = address
            # TODO: It's ok to not have drivers?  Just let query fill out the info? 
            if not 'drivers' in manifest:
                self.parent.send_error("HarmonyDevice:init:%s: no drivers in manifest: " % (name,manifest))
                return False
            drivers = manifest['drivers']
            # Get the things we need from the drivers, the rest will be queried.
        elif config_data is not None:
            self.name      = config_data['name']
            self.address   = config_data['address'].lower()
        else:
            self.parent.send_error("HarmonyDevice:init:%s: One of manifest or config_data must be passed in." % (address))
            return False
        # Add the Device
        self.parent.logger.info("HarmonyDevice:init: Adding %s %s" % (self.name,self.address))
        super(HarmonyDevice, self).__init__(parent, self.address, self.name, primary, manifest)
        # Call query to pull in the params before adding the motion node.
        self.query();
        self.parent.logger.info("HarmonyDevice:init: Added hub device '%s' %s" % (self.name,self.address))

    def poll(self):
        return

    def long_poll(self):
        return
    
    _drivers = {
    }
    _commands = {
    }

    # The nodeDef id of this camers.
    node_def_id = 'd25080146'
