
#
# HarmonyServer
#
# This is the main Harmony Hub Node Server.  
#
# TODO:
#  - Need ability to re-read the config if it changes?  But that also means the
#    ISY needs to be restarted if the activities changed?
#  - Set all values on query in case ISY is restarted?
#

from polyglot.nodeserver_api import Node
from functools import partial
from harmony_hub_nodes import *
from harmony_hub_funcs import myint,long2ip
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR
import time

class HarmonyServer(Node):
    """ Node that contains the Main Harmony Hub Server settings """

    def __init__(self, parent, address, name, manifest=None, config_data=None):
        self.parent   = parent
        self.address  = address
        self.name     = name
        self.do_poll  = True
        self.l_info("init","address=%s, name='%s', manifest=%s" % (self.address, self.name, manifest))
        #
        # Set defaults.
        #
        # Number of Hubs we are managing
        self.num_hubs     = 0
        # Logger debug mode
        self.debug_mode   = 10
        # Polyglot long/short poll time defaults come from parent.
        self.shortpoll = parent.shortpoll
        self.longpoll  = parent.longpoll
        if address in manifest:
            drivers = manifest[address]['drivers']
            if 'GV4' in drivers:
                self.debug_mode = drivers['GV4']
            if 'GV5' in drivers:
                self.shortpoll = drivers['GV5']
            if 'GV6' in drivers:
                self.longpoll = drivers['GV6']
        super(HarmonyServer, self).__init__(parent, self.address, self.name, True, manifest)
        self.query();
        # TODO: Pass proper manifest..
        self._add_hubs(manifest,config_data)

    def query(self, **kwargs):
        """ Look for cameras """
        self.l_info("query","start")
        self.set_driver('GV1', VERSION_MAJOR)
        self.set_driver('GV2', VERSION_MINOR)
        self._set_shortpoll(self.shortpoll)
        self._set_longpoll(self.longpoll)
        self._set_num_hubs(self.num_hubs)
        self._set_debug_mode(self.debug_mode)
        self._set_st(time.time())
        self.poll()
        self.report_driver()
        self.l_info("query","done")
        return True

    def poll(self):
        """ Poll Does nothing  """
        #self.l_debug("poll","")
        return True

    def long_poll(self):
        """ Long Poll Send DON """
        now = time.time()
        self.l_debug("long_poll","now=%d" % (now))
        self._set_st(now)
        self.report_isycmd('DON')
        return

    def on_exit(self):
        return True
    
    def l_info(self, name, string):
        self.parent.logger.info("%s:%s:%s: %s" %  (self.node_def_id,self.address,name,string))
        
    def l_error(self, name, string):
        self.parent.logger.error("%s:%s:%s: %s" % (self.node_def_id,self.address,name,string))
        
    def l_warning(self, name, string):
        self.parent.logger.warning("%s:%s:%s: %s" % (self.node_def_id,self.address,name,string))
        
    def l_debug(self, name, string):
        self.parent.logger.debug("%s:%s:%s: %s" % (self.node_def_id,self.address,name,string))
        
    def _add_hubs(self,manifest,config_data):
        for key in config_data:
            if key != 'server' and key != 'info':
                hub = HarmonyHub(self.parent, True, address=key, manifest=manifest, config_data=config_data[key])
                self._set_num_hubs(self.num_hubs + 1)
        return

    def _set_st(self, value):
        return self.set_driver('ST', value, report=True)

    def _set_num_hubs(self, value):
        self.num_hubs = value
        self.l_info("_set_num_hubs","%d" % (self.num_hubs))
        self.set_driver('GV3', self.num_hubs, uom=25, report=True)
        return True
    
    def _set_debug_mode(self, value):
        """ Set the log debug level
              0  = All
              10 = Debug
              20 = Info
              30 = Warning
              40 = Error
              50 = Critical
        """
        self.debug_mode = value
        self.l_info("_set_debug_mode","%d" % (self.debug_mode))
        self.set_driver('GV4', self.debug_mode, uom=25, report=True)
        self.logger.setLevel(self.debug_mode)
        return True
    
    def _set_shortpoll(self, value):
        self.shortpoll = value
        self.parent.shortpoll = self.shortpoll
        self.l_info("_set_shortpoll","%d" % (self.shortpoll))
        self.set_driver('GV5', self.shortpoll, uom=25, report=True)
        return True
    
    def _set_longpoll(self, value):
        self.longpoll = value
        self.parent.longpoll = self.longpoll
        self.l_info("_set_longpoll","%d" % (self.longpoll))
        self.set_driver('GV6', self.longpoll, uom=25, report=True)
        return True
    
    def _cmd_set_st(self, **kwargs):
        self._set_st(time.time())

    def _cmd_set_debug_mode(self, **kwargs):
        return self._set_debug_mode(myint(kwargs.get("value")))

    def _cmd_set_shortpoll(self, **kwargs):
        return self._set_shortpoll(myint(kwargs.get("value")))
        
    def _cmd_set_longpoll(self, **kwargs):
        return self._set_longpoll(myint(kwargs.get("value")))
        
    def _cmd_refresh_config(self, **kwargs):
        # TODO: Re-read config and new add_hubs?
        return False
        
    _drivers = {
        'ST':  [0, 56, int, False],
        'GV1': [0, 56, float],
        'GV2': [0, 56, float],
        'GV3': [0, 25, myint],
        'GV4': [0, 25, myint],
        'GV5': [0, 25, myint],
        'GV6': [0, 25, myint],
    }
    """ Driver Details:
    GV1:   float:   Version of this code (Major)
    GV2:   float:   Version of this code (Minor)
    GV3: integer: Number of the number of hubs we manage
    GV4: integer: Loging Mode
    GV5: integer: shortpoll
    GV6: integer: longpoll
    """
    _commands = {
        'ST': _cmd_set_st,
        'QUERY': query,
        'REFRESH_CONFIG': _cmd_refresh_config,
        'SET_DEBUGMODE': _cmd_set_debug_mode,
        'SET_SHORTPOLL': _cmd_set_shortpoll,
        'SET_LONGPOLL':  _cmd_set_longpoll
    }

    _sends = {
        'DON': [None, None, None],
        'DOF': [None, None, None]
    }
    
    # The nodeDef id of this camers.
    node_def_id = 'HarmonyServer'
