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

    def __init__(self, parent, primary, manifest=None, name=None, id=None):
        self.parent    = parent
        self.primary   = primary
        # Device id in harmony is everything except the leading first character.
        self.id        = id
        self.name      = name
        # Add the d prefix for the node address
        self.address   = 'd'+id
        self.node_def_id = self.address
        self.do_poll   = False
        # Add the Device
        self.l_info("init","Adding device name=%s, address=%s, node_def_id=%s" % (self.name,self.address,self.node_def_id))
        super(HarmonyDevice, self).__init__(parent, self.address, self.name, primary, manifest)
        self.l_info("init","Added device name=%s, address=%s, node_def_id=%s" % (self.name,self.address,self.node_def_id))

    def l_info(self, name, string):
        self.parent.logger.info("Dev:%s:%s:%s:%s: %s"    % (self.primary.node_def_id,self.node_def_id,self.address,name,string))
        
    def l_error(self, name, string):
        self.parent.logger.error("Dev:%s:%s:%s:%s: %s"   % (self.primary.node_def_id,self.node_def_id,self.address,name,string))
        
    def l_warning(self, name, string):
        self.parent.logger.warning("Dev:%s:%s:%s:%s: %s" % (self.primary.node_def_id,self.node_def_id,self.address,name,string))
        
    def l_debug(self, name, string):
        self.parent.logger.debug("Dev:%s:%s:%s:%s: %s"   % (self.primary.node_def_id,self.node_def_id,self.address,name,string))
        
    def _get_button_name(self,index):
        """
        Convert from button/function index from nls to real name
        because pyharmony needs the name.
        """
        self.l_debug("_get_button_name","index=%d" % (index))
        # TODO: Make sure it's a valid index?
        return self.parent.poly.nodeserver_config['info']['functions'][index]['name']

    def _send_command_by_index(self,index):
        name = self._get_button_name(index)
        self.l_debug("_send_command_by_index","index=%d, name=%s" % (index,name))
        return self._send_command(name)

    def _send_command(self,name):
        self.l_debug("_send_command_by_name","name=%s" % (name))
        # Push it to the Hub
        if self.primary.client is None:
            self.l_error("_send_command_by_index","No Client for command '%s'." % (name))
            ret = False
        else:
            ret = self.primary.client.send_command(self.id,name)
            self.l_debug("_send_command_by_name","send_command %s,%s result=%s" % (str(self.id),name,str(ret)))
            # TODO: This always returns None :(
            ret = True
        return ret

    def _cmd_set_button(self, **kwargs):
        """ 
        This runs when ISY calls set button which passes the button index
        """
        index = myint(kwargs.get("value"))
        self.l_debug("_cmd_set_button","index=%d" % (index))
        return self._send_command_by_index(index)
    
    def _cmd_don(self, **kwargs):
        """ 
        This runs when ISY calls set button which passes the button index
        """
        self.l_debug("_cmd_don","")
        # TODO: If no PowerOn command, do PowerToggle
        return self._send_command('PowerOn')
    
    def _cmd_dof(self, **kwargs):
        """ 
        This runs when ISY calls set button which passes the button index
        """
        self.l_debug("_cmd_dof","")
        # TODO: If no PowerOn command, do PowerToggle
        return self._send_command('PowerOff')
    
    _drivers = {
    }
    _commands = {
        'SET_BUTTON': _cmd_set_button,
        'DON': _cmd_don,
        'DOF': _cmd_dof,
    }

    # The nodeDef id of this camers.
    node_def_id = 'DeviceDefault'
