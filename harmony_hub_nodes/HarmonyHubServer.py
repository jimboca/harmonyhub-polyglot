
#
# HarmonyHubServer
#
# This is the main Harmony Hub Node Server.  
#
# TODO:
#  - Need ability to re-read the config if it changes?  But that also means the
#    ISY needs to be restarted if the activities changed?
#

from polyglot.nodeserver_api import Node
from functools import partial
from harmony_hub_nodes import *
from harmony_hub_funcs import myint,long2ip
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR
import time

class HarmonyHubServer(Node):
    """ Node that contains the Main Harmony Hub Server settings """

    def __init__(self, parent, address, name, manifest=None, config_data=None):
        self.parent   = parent
        self.address  = address
        self.name     = name
        self.parent.logger.info("HarmonyHubServer:init: address=%s, name='%s'" % (self.address, self.name))
        # Number of Hubs we are managing
        num_hubs     = 0
        debug_mode   = 10
        self._next_beat_t = 0
        if address in manifest:
            drivers = manifest[address]['drivers']
            if 'GV4' in drivers:
                debug_mode = drivers['GV4']
        super(HarmonyHubServer, self).__init__(parent, self.address, self.name, True, manifest)
        self.set_driver('GV1', VERSION_MAJOR, uom=56, report=False)
        self.set_driver('GV2', VERSION_MINOR, uom=56, report=False)
        self._set_num_hubs(num_hubs)
        self._set_debug_mode(debug_mode)
        self._st()
        self.report_driver()
        # TODO: Pass proper manifest..
        self._add_hubs(None,config_data)
        self.query();

    def _add_hubs(self,manifest,config_data):
        for key in config_data:
            if key != 'server' and key != 'info':
                hub = HarmonyHub(self.parent, True, address=key, manifest=None, config_data=config_data[key])
                self._set_num_hubs(self.num_hubs + 1)
        return

    def _st(self, **kwargs):
        return self.set_driver('ST', time.time(), report=True)

    def query(self, **kwargs):
        """ Look for cameras """
        self.parent.logger.info("HarmonyHubServer:query:start")
        self.parent.logger.debug("HarmonyHubServer:query:done")
        return True

    def poll(self):
        """ Poll Send DON every 60 seconds or so  """
        now = time.time()
        if now > self._next_beat_t:
            self._next_beat_t = now + 60
            self.set_driver('ST', now, report=True)
            self.report_isycmd('DON')
        return True

    def long_poll(self):
        """ Long Poll Nothing  """
        return

    def _set_num_hubs(self, value):
        self.num_hubs = value
        self.parent.logger.info("HarmonyHubServer:_set_num_hubs: %d" % (self.num_hubs))
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
        self.parent.logger.info("HarmonyHubServer:_set_debug_mode: %d" % (self.debug_mode))
        self.set_driver('GV4', self.debug_mode, uom=25, report=True)
        self.logger.setLevel(self.debug_mode)
        return True
    
    def _cmd_set_debug_mode(self, **kwargs):
        self._set_debug_mode(myint(kwargs.get("value")))
    
    _drivers = {
        'ST':  [0, 56, int, False],
        'GV1': [0, 56, float],
        'GV2': [0, 56, float],
        'GV3': [0, 25, myint],
        'GV4': [0, 25, myint],
        'GV5': [0, 56, float],
    }
    """ Driver Details:
    GV1:   float:   Version of this code (Major)
    GV2:   float:   Version of this code (Minor)
    GV3: integer: Number of the number of hubs we manage
    GV4: integer: Loging Mode
    """
    _commands = {
        'ST': _st,
        'QUERY': query,
        'SET_DEBUGMODE': _cmd_set_debug_mode,
    }

    _sends = {
        'DON': [None, None, None]
    }
    
    # The nodeDef id of this camers.
    node_def_id = 'HarmonyHubServer'
