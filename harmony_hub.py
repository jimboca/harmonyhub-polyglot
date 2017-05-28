#!/usr/bin/python
#
# Install:
#  sudo pip install pyharmony
# Issues:
#
# TODO: Cleanup logger routines, change all modules to call send_error in l_error.
#
""" Harmony Hub Node Server for ISY """

from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from harmony_hub_nodes import HarmonyServer
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR


class HarmonyHubNodeServer(SimpleNodeServer):
    """ Harmony Hub Node Server """
    
    def setup(self):
        """ Initial node setup. """
        super(SimpleNodeServer, self).setup()
        self.l_info('init','Version=%s.%s starting up.' % (VERSION_MAJOR,VERSION_MINOR))
        self.l_info('init',"Sandbox=%s" % (self.poly.sandbox))
        if int(self.poly.pgapiver) < 1:
            msg = "Polyglot version %s api version %s is to old, must be api version >= 1" % (self.poly.pgver,self.poly.pgapiver);
            self.l_error("init",msg)
            raise ValueError(msg)
        self.l_info('init',"pgver=%s" % (self.poly.pgver))
        self.l_info('init',"pgapiver=%s" % (self.poly.pgapiver))
        #self.l_debug('init',"Config=%s" % (self.config))
        # Setup the config data.
        self.get_hub_config()
        # define nodes for settings
        self.manifest = self.config.get('manifest', {})
        # Add the top level camera server node.
        HarmonyServer(self, self.poly.nodeserver_config['server']['node'],
                      self.poly.nodeserver_config['server']['name'], self.manifest, self.poly.nodeserver_config)
        self.update_config()

    def get_hub_config(self):
        """
        Read the config.
        TODO: Make sure they have run gmake config.
        """
        self.l_info('config',"NSConfig=%s" % (self.poly.nodeserver_config))
        save = False
        if (self.poly.nodeserver_config is None):
            self.l_error("No config data, must create config and generate profile")
        if save:
            # Not currently used, but here in case we ever edit the config and need to save.
            self.logger.info('config',"Saving Changes NSConfig=%s" % (self.poly.nodeserver_config))
            self.write_nodeserver_config()

    # For others to call
    def write_nodeserver_config(self):
        self.l_info("write_nodeserver_config",
                    ": config=%s" % (self.poly.nodeserver_config))
        self.poly.write_nodeserver_config()
        
    def poll(self):
        """ Poll Hubs's  """
        self.l_debug("poll","")
        for node_addr, node in self.nodes.items():
            if node.do_poll:
                self.l_debug("poll","child %s" % (str(node_addr)))
                node.poll()
        return True

    def long_poll(self):
        """ Call long_poll on all nodes and Save configuration every 30 seconds. """
        self.l_debug("long_poll","")
        self.update_config()
        for node_addr, node in self.nodes.items():
            if node.do_poll:
                self.l_debug("long_poll","child %s" % (str(node_addr)))
                node.long_poll()
        return True

    def on_exit(self, **kwargs):
        # TODO: Close each hub client.
        self.update_config()
        for node_addr, node in self.nodes.items():
            if node.do_poll:
                self.l_debug("on_exit","child %s" % (str(node_addr)))
                node.on_exit()
        return True

    def send_error(self,error_str):
        self.poly.send_error(error_str);

    def l_info(self, name, string):
        self.logger.info("Main:%s: %s" %  (name,string))
        
    def l_error(self, name, string):
        # Print in my log and the polyglot log.
        error_s = "Main:%s: %s" % (name,string)
        self.logger.error(error_s)
        self.send_error(error_s)
        
    def l_warning(self, name, string):
        self.logger.warning("Main:%s: %s" % (name,string))
        
    def l_debug(self, name, string):
        self.logger.debug("Main:%s: %s" % (name,string))

def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = HarmonyHubNodeServer(poly, shortpoll=30, longpoll=300)
    poly.connect()
    poly.wait_for_config()
    nserver.setup()
    nserver.run()


if __name__ == "__main__":
    main()
