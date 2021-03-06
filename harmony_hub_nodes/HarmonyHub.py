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
from pyharmony import ha_get_token,ha_get_client
from traceback import format_exception

class HarmonyHub(Node):
    """ 
    The Main Node for a single Harmony Hub
    """

    def __init__(self, parent, primary, manifest=None, config_data=None, address=None):
        self.parent      = parent
        self.connected   = 0
        self.do_poll     = False
        self.current_activity = -2
        if config_data is None:
            self.parent.send_error("%s config_data must be passed in." % (address))
            self.l_error("init","config_data must be passed in.")
            return False
        else:
            # Gotta have an address
            if address is None:
                self.parent.send_error("HarmonyHub:init:%s: address not passed in")
                return False
            # The node_def_id is the address because each hub has a unique nodedef in the profile.
            self.node_def_id = address
            self.name        = config_data['name']
            self.address     = address.lower()
            self.host        = config_data['host']
            self.port        = 5222
        if manifest is not None:
            # TODO: Do we need to use any manifest data?  Check for nodes that already exist?
            self.l_debug("init","Nothing is currently used from passed in manifest")
        # Add the Hub
        self.l_info("init","Adding name=%s address=%s host=%s" % (self.name, self.address, self.host))
        super(HarmonyHub, self).__init__(parent, self.address, self.name, primary, manifest)
        # Initialize what we need defined
        self.token  = None
        self.client = None
        self._set_st(0)
        # Connect to the hub
        self._get_client()
        # Setup activities and devices
        self.init_activities_and_devices()
        # Call query to initialize and pull the info from the hub.
        self.query();
        # Only Hub devices are polled.
        self.do_poll     = True
        self.l_info("init","done adding hub '%s' '%s' %s" % (self.address, self.name, self.host))

    def query(self, **kwargs):
        """ query the hub """
        self.l_debug("query","start")
        # TODO: Trap ip2long failure when bad address is specified.
        self.set_driver('GV1',  ip2long(self.host), uom=56, report=True)
        self.set_driver('GV2',  self.port, uom=56, report=True)
        # This forces current activity to update.
        self.current_activity = -2
        self._set_st(self.st)
        self.poll()
        self.l_debug("query","done")
        return True

    def poll(self):
        self.l_debug("poll","start")
        # If we had a connection issue previously, try to fix it.
        if self.st == 0:
            self.l_debug("poll","Calling get_client st=%d" % (self.st))
            if not self._get_client():
                return False
        self._get_current_activity()
        self.l_debug("poll","done")
        return True

    def long_poll(self):
        return True

    def on_exit(self):
        if self.client is not None:
            self.client.disconnect(send_close=True)

    def l_info(self, name, string):
        self.parent.logger.info("Hub:%s:%s: %s" %  (self.node_def_id,name,string))
        
    def l_error(self, name, string):
        self.parent.logger.error("Hub:%s:%s: %s" % (self.node_def_id,name,string))
        
    def l_warning(self, name, string):
        self.parent.logger.warning("Hub:%s:%s: %s" % (self.node_def_id,name,string))
        
    def l_debug(self, name, string):
        self.parent.logger.debug("Hub:%s:%s: %s" % (self.node_def_id,name,string))

    def _get_client(self):
        self.l_info("get_client","Initializing PyHarmony Client")
        try:
            self.token  = ha_get_token(self.host, self.port)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_str = ''.join(format_exception(exc_type, exc_value, exc_traceback))
            self.l_error("get_client",err_str)
            self._set_st(0)
            return False
        self.l_info("get_client","PyHarmony token= " + str(self.token))
        try:
            self.client = ha_get_client(self.token, self.host, self.port)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_str = ''.join(format_exception(exc_type, exc_value, exc_traceback))
            self.l_error("get_client",err_str)
            self._set_st(0)
            return False
        self._set_st(1)
        self.l_info("get_client","PyHarmony client= " + str(self.client))
        return True

    def _get_current_activity(self):
        try:
            ca = self.client.get_current_activity()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            err_str = ''.join(format_exception(exc_type, exc_value, exc_traceback))
            self.l_error("get_current_activity",err_str)
            self._set_st(0)
            return False
        self._set_st(1)
        self.l_debug("poll","client.get_current_activity=%s" % str(ca))
        self._set_current_activity(ca)
        
    def _set_st(self, value):
        self.st = value
        return self.set_driver('ST', value, report=True)

    def init_activities_and_devices(self):
        self.activity_nodes = dict()
        self.device_nodes = dict()
        harmony_config = self.client.get_config()
        for a in harmony_config['activity']:
            if a['id'] != '-1':
                self.l_info("init","Activity: %s  Id: %s" % (a['label'], a['id']))
                self.add_activity(a['label'], a['id'])
        for d in harmony_config['device']:
            self.l_info("init","Device '%s' '%s', Type=%s, Manufacturer=%s, Model=%s" % (d['id'],d['label'],d['type'],d['manufacturer'],d['model']))
            # TODO: Remove the d, and let Device add it back.
            self.add_device(d['label'],d['id'])
            
    def add_device(self,name,id):
        # TODO: Pass in name and address as optional args.
        node = HarmonyDevice(self.parent, self, manifest=None, name=name, id=id)
        self.device_nodes[node.address] = node
        return node;

    def add_activity(self,name,number):
        node = HarmonyActivity(self.parent, self, name=name, number=number)
        self.activity_nodes[number] = node
        return node;

    def start_activity(self, id=False, index=False):
        """ 
        Start the activity
        """
        if index is False and id is False:
            self.l_error("start_activity","Must pass id or index")
            return False
        if index is False:
            index = self._get_activity_index(id)
        elif id is False:
            id = self._get_activity_id(index)
        self.l_debug("start_activity"," id=%s index=%s" % (str(id),str(index)))
        if self.client is None:
            self.l_error("start_activity","No Client" )
            ret = False
        else:
            if id != -1:
                ret = self.client.start_activity(id)
                self.l_debug("start_activity","id=%s result=%s" % (str(id),str(ret)))
            else:
                ret = self.client.power_off()
                self.l_debug("start_activity","power_off result=%s" % (str(ret)))
            if ret:
                # it worked, push it back to polyglot
                self._set_current_activity(id)
        return ret

    def end_activity(self, id=False, index=False):
        """ 
        End the activity
        """
        if self.client is None:
            self.l_error("end_activity","No Client" )
            ret = False
        else:
            # Only way to end, is power_off (activity = -1)
            ret = self.client.power_off()
            # TODO: Currently released version of pyharmony always returns None
            # TODO: remove this if a new version is released.
            ret = True
            self.l_debug("end_activity","ret=%s" % (str(ret)))
            if ret:
                self._set_current_activity(-1)
        return ret
            
    def _set_all_activities(self,val,ignore_id=False):
        # All other activities are no longer current
        for nid in self.activity_nodes:
            if ignore_id is False:
                self.activity_nodes[nid]._set_st(val)
            else:
                if int(nid) != int(ignore_id):
                    self.activity_nodes[nid]._set_st(val)
        
    def _get_activity_id(self,index):
        """
        Convert from activity index from nls, to real activity number
        """
        self.parent.logger.debug("HarmonyHub:_get_activity_id:%s: %d" % (self.address,index))
        return self.parent.poly.nodeserver_config['info']['activities'][index]['id']
    
    def _get_activity_index(self,id):
        """
        Convert from activity index from nls, to real activity number
        """
        self.l_debug("_get_activity_index", str(id))
        cnt = 0
        for a in self.parent.poly.nodeserver_config['info']['activities']:
            if int(a['id']) == int(id):
                return cnt
            cnt += 1
        self.l_error("_get_activity_index","No activity id %s found." % (str(id)))
        # Print them out for debug
        for a in self.parent.poly.nodeserver_config['info']['activities']:
            self.l_error("_get_activity_index","  From: label=%s, id=%s" % (a['label'],a['id']))
        return False
    
    def change_channel(self,channel):
        self.l_debug("change_channel","channel=%s" % (channel))
        # Push it to the Hub
        if self.client is None:
            self.l_error("change_channel","No Client for channel '%s'." % (channel))
            ret = False
        else:
            ret = self.client.change_channel(channel)
            self.l_debug("change_channel","%s result=%s" % (channel,str(ret)))
            # TODO: This always returns False :(
            ret = True
        return ret

    def _set_current_activity(self, id, force=False):
        """ 
        Update Polyglot with the current activity.
        """
        val   = myint(id)
        if self.current_activity == val:
            return True
        # The harmony activity number
        self.current_activity = val
        index = self._get_activity_index(val)
        self.l_info("_set_current_activity","activity=%d, index=%d" % (self.current_activity,index))
        self.set_driver('GV3', index, uom=25, report=True)
        # Make the activity node current, unless it's -1 which is poweroff
        ignore_id=False
        if id != -1:
            self.activity_nodes[str(id)]._set_st(1)
            ignore_id=id
        # Update all the other activities to not be the current.
        self._set_all_activities(0,ignore_id=ignore_id)
        return True

    def _cmd_set_current_activity(self, **kwargs):
        """ 
        This runs when ISY changes the current current activity
        """
        index = myint(kwargs.get("value"))
        return self.start_activity(index=index)
        
    def _cmd_change_channel(self, **kwargs):
        """ 
        This runs when ISY calls set button which passes the button index
        """
        channel = myint(kwargs.get("value"))
        self.l_debug("_cmd_change_channel","channel=%d" % (channel))
        return self.change_channel(channel)

    def _cmd_off(self, **kwargs):
        """
        This runs when ISY calls Off or Fast Off and sets the activity to poweroff
        """
        self.l_debug("_cmd_off","activity=%d" % (self.current_activity))
        return self.end_activity()
    
    _drivers = {
        'ST':  [0, 2,  myint],
        'GV1': [0, 56, myint],
        'GV2': [0, 56, myint],
        'GV3': [0, 25, myint],
        'GV4': [0, 56, myint],
        'GV5': [0, 56, myint],
    }
    """ Driver Details:
    ST:   boolean: Responding
    GV1:  unsigned integer: IP Address
    GV2:  integer: Port
    GV3:  integer: Current Activity
    """
    _commands = {
        'QUERY': query,
        'SET_ACTIVITY': _cmd_set_current_activity,
        'CHANGE_CHANNEL': _cmd_change_channel,
        'DOF': _cmd_off,
        'DFOF': _cmd_off,
    }

    # The nodeDef id of this camers.
    node_def_id = 'HubDefault'
