#!/usr/bin/python
#
# Install:
#  sudo pip install pyharmony
# Issues:
#
#
""" Harmony Hub Node Server for ISY """

from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
#from collections import defaultdict, OrderedDict
#import os, json, logging, requests, threading, SocketServer, re, socket, yaml
#from requests.auth import HTTPDigestAuth,HTTPBasicAuth
from harmony_hub_nodes import HarmonyHubServer
from harmony_hub_polyglot_version import VERSION_MAJOR,VERSION_MINOR


class HarmonyHubNodeServer(SimpleNodeServer):
    """ Harmony Hub Node Server """
    
    def setup(self):
        """ Initial node setup. """
        super(SimpleNodeServer, self).setup()
        self.logger.info('HarmonyHubNodeServer: Version=%s.%s starting up.' % (VERSION_MAJOR,VERSION_MINOR))
        self.logger.info("HarmonyHubNodeServer: Sandbox=%s" % (self.poly.sandbox))
        self.logger.info("HarmonyHubNodeServer: Config=%s" % (self.config))
        self.logger.info("HarmonyHubNodeServer: Config=%s" % (self.config))
        # Setup the config data.
        self.get_hub_config()
        # define nodes for settings
        self.manifest = self.config.get('manifest', {})
        # Add the top level camera server node.
        HarmonyHubServer(self, self.poly.nodeserver_config['server']['node'],
                         self.poly.nodeserver_config['server']['name'], self.manifest, self.poly.nodeserver_config)
        self.update_config()

    # TODO: Convert this to use new polyglot config?
    def get_hub_config(self):
        """
        Read the sandbox/config.yaml.
        If it does not exist, create a blank template
        Make sure necessary settings are set
        """
        self.logger.info("HarmonyHubNodeServer:get_hub_config: NSConfig=%s" % (self.poly.nodeserver_config))
        save = False
        if (self.poly.nodeserver_config is None):
            self.poly.nodeserver_config = {
                'server' : { 'node' : 'harmonyhubserver', 'name' : 'HarmonyHub Server' },
                'YourHarmonyName' : { 'name' : 'Your Harmony Node Name', 'host' : 'xxx.xxx.xxx.xxx' }
            }
            self.logger.info("HarmonyHubNodeServer:get_hub_config: Using Default config=%s"
                             % (self.poly.nodeserver_config))
            save = True
        if 'server' in self.poly.nodeserver_config and self.poly.nodeserver_config['server'] is not None:
            if not 'name' in self.poly.nodeserver_config['server'] or self.poly.nodeserver_config['server']['name'] is None:
                self.poly.nodeserver_config['server']['name'] = "HarmonyHub Server"
                save = True
            if not 'node' in self.poly.nodeserver_config['server'] or self.poly.nodeserver_config['server']['node'] is None:
                self.poly.nodeserver_config['server']['node'] = "harmonyhub"
                save = True
        if save:
            self.logger.info("HarmonyHubNodeServer:get_hub_config: Saving Changes NSConfig=%s" % (self.poly.nodeserver_config))
            self.write_nodeserver_config()

    # For others to call
    def write_nodeserver_config(self):
        self.logger.info("HarmonyHubNodeServer:write_nodeserver_config: config=%s"
                         % (self.poly.nodeserver_config))
        self.poly.write_nodeserver_config()
        
    def poll(self):
        """ Poll Hubs's  """
        for node_addr, node in self.nodes.items():
            node.poll()
        return True

    def long_poll(self):
        """ Call long_poll on all nodes and Save configuration every 30 seconds. """
        self.logger.debug("HarmonyHubNodeServer:long_poll")
        self.update_config()
        for node_addr, node in self.nodes.items():
            node.long_poll()
        return True

    def on_exit(self, **kwargs):
        return True

    def send_error(self,error_str):
        self.logger.error(error_str)
        self.poly.send_error(error_str);
        
def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = HarmonyHubNodeServer(poly, shortpoll=60, longpoll=360)
    poly.connect()
    poly.wait_for_config()
    nserver.setup()
    nserver.run()


if __name__ == "__main__":
    main()
