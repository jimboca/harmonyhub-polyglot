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
        self.parent      = parent
        self.parent.logger.info("HarmonyActivity:init: Adding manifest=%s name=%s number=%s" % (manifest,name,str(number)))
        self.status = {}
        # Use manifest values if passed in.
        if manifest is not None:
            # TODO: Support manifest
            self.name  = manifest['name']
        else:
            self.name      = name
            self.number    = number
            # Address is the activity number
            self.address   = 'a' + str(number)
        # Add the Activity
        self.parent.logger.info("HarmonyActivity:init: Adding %s, %s, %s" % (self.name,self.address,self.node_def_id))
        super(HarmonyActivity, self).__init__(parent, self.address, self.name, primary, manifest)
        self.set_driver('ST',   0, uom=25, report=True)
        self.parent.logger.info("HarmonyActivity:init: Added hub activity '%s', %s, %s" % (self.name,self.address,self.node_def_id))

    def set_st(self, st):
        self.set_driver('ST',   int(st), uom=25, report=True)
        self.parent.logger.debug("HarmonyActivity:set_st:%s: set=%s, get=%s" % (self.name,st,self.get_driver('ST')[0]))
        
    def _cmd_on(self, **kwargs):
        """ 
        This runs when ISY calls on button
        """
        self.parent.logger.debug("HarmonyActivity:_cmd_on:%s:" % (self.address))
        # Push it to the Hub
        ret = self.primary.start_activity(id=self.number)
        self.parent.logger.debug("HarmonyActivity:_cmd_on:%s: ret=%s" % (self.address,str(ret)))
        if ret:
            self.set_st(1)
        return ret

    def _cmd_off(self, **kwargs):
        """ 
        This runs when ISY calls on button
        """
        self.parent.logger.debug("HarmonyActivity:_cmd_off:%s:" % (self.address))
        # Push it to the Hub
        ret = self.primary.end_activity(id=self.number)
        self.parent.logger.debug("HarmonyActivity:_cmd_off:%s: ret=%s" % (self.address,str(ret)))
        if ret:
            self.set_st(0)
        return ret

    def poll(self):
        return

    def long_poll(self):
        return
    
    _drivers = {
        'ST':  [0, 25,  myint],
    }
    _commands = {
        'ON': _cmd_on,
        'OFF': _cmd_off,
    }

    # The nodeDef id of this activity.
    node_def_id = 'HarmonyActivity'
