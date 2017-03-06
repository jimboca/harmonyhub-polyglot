#
# TODO:
#
#

import os,sys
from polyglot.nodeserver_api import Node
from harmony_hub_funcs import myint

class HarmonyActivity(Node):
    """ 
    The Main Node for a single Harmony Hub
    """

    def __init__(self, parent, primary, manifest=None, name=None, number=None):
        self.parent    = parent
        self.primary   = primary
        self.name      = name
        self.number    = number
        self.do_poll   = False
        # Address is the activity number
        self.address   = 'a' + str(number)
        # Add the Activity
        self.l_info("init","Adding activity name=%s, address=%s" % (self.name,self.address))
        super(HarmonyActivity, self).__init__(parent, self.address, self.name, primary, manifest)
        # TODO: Hack, to force a state change on startup.
        self._set_st(1)
        self._set_st(0)
        self.l_info("init","Added activity name=%s adress=%s" % (self.name,self.address))

    def query(self, **kwargs):
        self._set_st(self.st)
        return True
        
    def l_info(self, name, string):
        self.parent.logger.info("Act:%s:%s:%s: %s" %  (self.primary.node_def_id,self.address,name,string))
        
    def l_error(self, name, string):
        self.parent.logger.error("Act:%s:%s:%s: %s" % (self.primary.node_def_id,self.address,name,string))
        
    def l_warning(self, name, string):
        self.parent.logger.warning("Act:%s:%s:%s: %s" % (self.primary.node_def_id,self.address,name,string))
        
    def l_debug(self, name, string):
        self.parent.logger.debug("Act:%s:%s:%s: %s" % (self.primary.node_def_id,self.address,name,string))
        
    def _set_st(self, st):
        self.st = st
        self.set_driver('ST', int(st), uom=25, report=True)
        self.l_debug("_set_st","set=%s, get=%s" % (st,self.get_driver('ST')[0]))
        
    def _cmd_on(self, **kwargs):
        """ 
        This runs when ISY calls on button
        """
        self.l_debug("_cmd_on","")
        # Push it to the Hub
        ret = self.primary.start_activity(id=self.number)
        self.l_debug("_cmd_on","ret=%s" % (str(ret)))
        if ret:
            self._set_st(1)
        return ret

    def _cmd_off(self, **kwargs):
        """ 
        This runs when ISY calls on button
        """
        self.l_debug("_cmd_off","")
        # Push it to the Hub
        ret = self.primary.end_activity(id=self.number)
        self.l_debug("_cmd_off","ret=%s" % (str(ret)))
        if ret:
            self._set_st(0)
        return ret

    _drivers = {
        'ST':  [0, 25,  myint],
    }
    _commands = {
        'QUERY': query,
        'DON': _cmd_on,
        'DOF': _cmd_off,
    }

    # The nodeDef id of this activity.
    node_def_id = 'HarmonyActivity'
