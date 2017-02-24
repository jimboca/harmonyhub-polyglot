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
            self.node_def_id = self.address
            # Device id in harmony is everything except the leading first character.
            self.id          = self.address[1:]
        else:
            self.parent.send_error("HarmonyDevice:init:%s: One of manifest or config_data must be passed in." % (address))
            return False
        # Add the Device
        self.parent.logger.info("HarmonyDevice:init: Adding %s, %s, %s" % (self.name,self.address,self.node_def_id))
        super(HarmonyDevice, self).__init__(parent, self.address, self.name, primary, manifest)
        self.parent.logger.info("HarmonyDevice:init: Added hub device '%s', %s, %s" % (self.name,self.address,self.node_def_id))

    def _get_button_name(self,index):
        """
        Convert from button/function index from nls to real name
        """
        self.parent.logger.debug("HarmonyDevice:_get_button_number:%s: %d" % (self.address,index))
        return self.parent.poly.nodeserver_config['info']['functions'][index]['name']
        
    def _cmd_set_button(self, **kwargs):
        """ 
        This runs when ISY calls set button
        """
        index = myint(kwargs.get("value"))
        self.parent.logger.debug("HarmonyDevice:_cmd_set_button:%s: %d" % (self.address,index))
        name = self._get_button_name(index)
        self.parent.logger.debug("HarmonyDevice:_cmd_set_button:%s: %s" % (self.address,name))
        # Push it to the Hub
        if self.primary.client is None:
            self.parent.logger.error("HarmonyHub:_cmd_set_button:%s: No Client" % (self.address))
            ret = False
        else:
            ret = self.primary.client.send_command(self.id,name)
            self.parent.logger.debug("HarmonyHub:_cmd_set_button:%s: send_command=%s result=%s" % (self.address,name,str(ret)))
        return ret

    def poll(self):
        return

    def long_poll(self):
        return
    
    _drivers = {
    }
    _commands = {
        'SET_BUTTON': _cmd_set_button,
    }

    # The nodeDef id of this camers.
    node_def_id = 'DeviceDefault'
